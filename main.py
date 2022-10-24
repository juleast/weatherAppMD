# kivymd imports
import atexit

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton

# kivy imports
from kivy import require
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.properties import OptionProperty
from kivy.uix.screenmanager import FallOutTransition, RiseInTransition
from kivy.loader import Loader
# others
from plyer import gps
from geopy.geocoders import Nominatim

# local imports
from tools.apicall import WeatherData, GeoLoc
from tools.check import internet, filecheck
from tools.filemanager import rw
import dialog.contents as c
from threading import Thread
from functools import partial

# some misc options
Loader.loading_image = "./assets/images/bg/25501.jpg"
require('2.1.0')
Window.softinput_mode = 'below_target'
geolocator = Nominatim(user_agent="simple-weather")

# load the kv files
Builder.load_file('weather.kv')

# variables for special characters and units
units = {'metric': ["°C", "km/h", "c"], 'us': ["°F", "mph", "f"]}
degree = "°"
# variable for permission status
permission = ["ungranted"]
# backup variable for location
b_location = GeoLoc().fetch()


# dialog class to add an option to change button direction
class MDDialog(MDDialog):
    button_direction = OptionProperty(
        "right", options=["left", "right", "center"]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ids.root_button_box.anchor_x = self.button_direction


# the main screen widget
class MainScreen(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # some init variables
        self.def_location = None
        self.unit = None
        self.prev = None
        self.location = ""
        self.coords = ""
        self.no_gps = False
        # popup dialog for changing locations
        self.picker = MDDialog(
            title="Change location",
            type="custom",
            content_cls=c.Picker(),
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.cancel(self.picker)
                ),
                MDRaisedButton(
                    text="SAVE",
                    on_release=lambda x: self.reload()
                )
            ],
        )
        '''The 6 variables below are popup dialogs'''
        # popup dialog for setting default location
        self.def_picker = MDDialog(
            title="Set default location",
            type="custom",
            content_cls=c.Picker(),
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.cancel(self.def_picker)
                ),
                MDRaisedButton(
                    text="SAVE",
                    on_release=lambda x: self.save()
                )
            ]
        )
        # popup dialog for setting default measurement unit
        self.unit_picker = MDDialog(
            title="Change weather unit",
            type="custom",
            content_cls=c.UnitChanger(),
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=MainApp().theme_cls.primary_color,
                    on_release=lambda x: self.unit_change()
                )
            ],
            button_direction="center"
        )
        # popup dialog to show error message
        self.weather_error = MDDialog(
            type="custom",
            content_cls=c.Error(),
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=MainApp().theme_cls.primary_color,
                    on_release=lambda x: self.weather_error.dismiss()
                )
            ],
            button_direction="center",
        )
        # popup dialog to show internet error
        self.internet_error = MDDialog(
            type="custom",
            content_cls=c.ConError(),
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=MainApp().theme_cls.primary_color,
                    on_release=lambda x: self.internet_error.dismiss()
                )
            ],
            button_direction="center",
        )
        # popup dialog to show gps permission error
        self.gps_error = MDDialog(
            title="Please allow location permissions",
            type="custom",
            content_cls=c.GPSError(),
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="Grant permissions",
                    theme_text_color="Custom",
                    text_color=MainApp().theme_cls.primary_color,
                    on_release=lambda x: self.regrant_perms()
                )
            ],
            button_direction="center"
        )
        # popup to show loading message
        self.loading = MDDialog(
            type="custom",
            content_cls=c.GPSLoading(),
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="I don't have GPS",
                    theme_text_color="Custom",
                    text_color=MainApp().theme_cls.accent_color,
                    on_release=lambda x: Clock.schedule_once(self.set_gps)
                )
            ],
            button_direction="center"
        )
        # popup to show credits
        self.credits = MDDialog(
            type="custom",
            content_cls=c.Credits(),
            auto_dismiss=True,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=MainApp().theme_cls.primary_color,
                    on_release=lambda x: self.credits.dismiss()
                )
            ],
            button_direction="center"
        )
        # popup to show support options
        self.support = MDDialog(
            type="custom",
            content_cls=c.Support(),
            auto_dismiss=True,
            buttons=[
                MDFlatButton(
                    text="CLOSE",
                    theme_text_color="Custom",
                    text_color=MainApp().theme_cls.primary_color,
                    on_release=lambda x: self.support.dismiss()
                )
            ],
            button_direction="center"
        )
        Clock.schedule_once(self.request_android_permissions, 4)

    # not to be confused with the class initializer; a function to initialize data for the app
    def init(self, *args):
        # checks if location permissions have been granted
        if permission[0] == "granted":
            # checks if there is a save file available
            if filecheck().file():
                r = rw()
                rd = r.read()
                # initial required variables for weather data
                self.location = rd['location']
                self.unit = rd['unit']
                print("File exists. Using existing variables...")
            else:
                x = 0
                # configure the gps locator
                gps.configure(on_location=self.get_location)
                self.start()
                Thread(target=self.open_load, args=(), daemon=True).start()
                while self.coords == "":
                    print("Coordinates: ", self.coords)
                    if self.no_gps:
                        break
                # checks if there was a GPS response versus user interruption
                if self.no_gps:
                    print("Looks like GPS failed. Using GeoIP.")
                    if b_location != -1:
                        self.location = b_location
                    else:
                        self.location = "Newmarket, Ontario"
                else:
                    Thread(target=self.close_load, args=(), daemon=True).start()
                    print("GPS successful. Program will use this data for weather.")
                    # save gps location data
                    location = geolocator.reverse(self.coords).raw
                    city = location['address']['city']
                    region = location['address']['state']
                    self.location = f"{city},{region}"
                self.unit = "metric"
            self.prev = ""
            # variables to store in the json file
            self.def_location = self.location
            # change data on settings page for initial
            self.def_picker.content_cls.ids.current_location.text = f"{self.location}"
            self.picker.content_cls.ids.current_location.text = f"{self.location}"
            if self.unit == "metric":
                self.unit_picker.content_cls.ids.unit_switch.active = False
            else:
                self.unit_picker.content_cls.ids.unit_switch.active = True
            # save initial collected data
            self.save_settings()
            # runs the update function
            Clock.schedule_once(self.get_update)

    # these methods are for opening and closing the loading dialog
    @mainthread
    def open_load(self):
        self.loading.open()

    @mainthread
    def close_load(self):
        self.loading.dismiss()

    '''Related to GPS'''

    # method to request location permissions of device
    def request_android_permissions(self, *args):
        from android.permissions import Permission, request_permissions

        def callback(permissions, results):
            if all([res for res in results]):
                print("All permissions granted.")
                permission[0] = "granted"
                Thread(target=self.init, args=(), daemon=True).start()
            else:
                @mainthread
                def error_open():
                    self.gps_error.open()

                error_open()

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)

    # method to grant location permissions
    def regrant_perms(self):
        self.gps_error.dismiss()
        self.request_android_permissions()

    # method to start collecting gps location data
    def start(self, *args):
        gps.start(minTime=500, minDistance=0)

    # method that will get the current gps location
    def get_location(self, **kwargs):
        lat = kwargs['lat']
        lon = kwargs['lon']
        gps.stop()
        self.coords = f"{lat}, {lon}"

    @mainthread
    # method to set no_gps to true
    def set_gps(self, *args):
        self.no_gps = True
        self.loading.dismiss()

    '''Related to core app functions'''

    # method that cancels unit change dialog
    def get_update(self, *args):
        Thread(target=self.update, args=(), daemon=True).start()

    # the main update method for screen
    @mainthread
    def update(self, *args):
        # checks for internet first
        if internet().ping():
            weather_today = WeatherData(self.location, units[self.unit][2]).now_fetch()
            weather_tmr = WeatherData(self.location, units[self.unit][2]).tmr_fetch()
            # check if a valid weather data has been returned
            if weather_today != -1 and weather_tmr != 1:
                self.today(self.unit, weather_today)
                self.tmr(self.unit, weather_tmr)
            else:
                self.weather_error.open()
                self.location = self.prev
                self.picker.content_cls.ids.current_location.text = f"{self.location}"
        else:
            print("Could not verify a valid internet connection")
            if self.prev != "":
                self.location = self.prev
            Clock.schedule_once(self.internet_error.open, 1)

    # method that updates today weather screen
    def today(self, unit, data):
        # update location title in topappbar
        self.ids.city_name.title = data['location']
        # update date
        self.ids.date.text = data["date"]
        # main today weather data values are updated here
        self.ids.temp_text.text = f"{data['main'][0]}{units[unit][0]}"
        self.ids.temp_feels.text = f"Feels like {data['main'][1]}{degree}"
        self.ids.temp_low.text = f"{data['main'][2]}{degree}"
        self.ids.temp_high.text = f"{data['main'][3]}{degree}"
        self.ids.weather_condition.text = data['main'][4]
        self.ids.weather_icon.source = f"./assets/icons/{data['main'][5]}.png"
        # misc today weather data values are updated here
        self.ids.weather_precip.text = f"{data['misc'][0]}%"
        self.ids.weather_wind.text = f"{data['misc'][1]} {units[unit][1]}"
        self.ids.weather_humid.text = f"{data['misc'][2]}%"

    # method that updates tmr weather screen
    def tmr(self, unit, data):
        # update date
        self.ids.date_tmr.text = data["date"]
        # main tmr weather data values are updated here
        self.ids.temp_low_tm.text = f"{data['main'][0]}{degree}"
        self.ids.temp_high_tm.text = f"{data['main'][1]}{degree}"
        self.ids.weather_condition_tm.text = data['main'][2]
        self.ids.weather_icon_tm.source = f"./assets/icons/{data['main'][3]}.png"
        # misc today weather data values are updated here
        self.ids.weather_precip_tm.text = f"{data['misc'][0]}%"
        self.ids.weather_wind_tm.text = f"{data['misc'][1]} {units[unit][1]}"
        self.ids.weather_humid_tm.text = f"{data['misc'][2]}%"

    # method that will set a new default location for the user the weather is not updated here
    def save(self):
        # makes sure that user has entered in (city,region) format
        test = self.def_picker.content_cls.ids.location.text.split(",")
        if self.def_picker.content_cls.ids.location.text != "" and len(test) == 2:
            capitalize = f"{test[0].title()},{test[1].title()}"
            self.def_location = capitalize
            self.def_picker.content_cls.ids.location.text = ""
            self.def_picker.dismiss()
            self.def_picker.content_cls.ids.location.helper_text = "Field cannot be blank"
            self.def_picker.content_cls.ids.current_location.text = f"{self.def_location}"
        else:
            self.def_picker.content_cls.ids.location.helper_text = "Must be (city, region) format"
            self.def_picker.content_cls.ids.location.error = True

    # method that will change weather measurement unit based on switch
    def unit_change(self):
        state = self.unit_picker.content_cls.ids.unit_switch.active
        if state:
            self.unit = "us"
        elif not state:
            self.unit = "metric"
        self.unit_picker.dismiss()

    # method that changes current weather location
    def reload(self):
        # makes sure that user has entered in (city,region) format
        test = self.picker.content_cls.ids.location.text.split(",")
        if self.picker.content_cls.ids.location.text != "" and len(test) == 2:
            # backups current city name to revert when errors occur
            self.prev = self.location
            capitalize = f"{test[0].title()},{test[1].title()}"
            self.location = capitalize
            self.picker.content_cls.ids.location.text = ""
            self.picker.dismiss()
            self.picker.content_cls.ids.current_location.text = f"{self.location}"
            self.picker.content_cls.ids.location.helper_text = "Field cannot be left blank"
            self.nav_drawer.set_state("close")
            self.update()
        else:
            self.picker.content_cls.ids.location.helper_text = "Must be (city,region) format"
            self.picker.content_cls.ids.location.error = True

    # clears text
    def clear_text(self, popup, *args):
        popup.content_cls.ids.location.text = ""

    # method to close location switcher popup and also clear text
    def cancel(self, popup, *args):
        popup.dismiss()
        popup.content_cls.ids.location.helper_text = "Field cannot be left blank"
        Clock.schedule_once(partial(self.clear_text, popup), .15)

    '''Related to switching screens'''

    # method that switches to the settings screen
    def open_settings(self):
        self.ids.screenmanager.transition = RiseInTransition(duration=0.2)
        self.ids.screenmanager.current = 'settings'
        self.nav_drawer.set_state("close")

    # method that switches to the main screen and saves any changes done in settings
    def open_main(self):
        self.ids.screenmanager.transition = FallOutTransition(duration=0.2)
        self.ids.screenmanager.current = "main"
        Thread(target=self.save_settings, args=(), daemon=True).start()

    def save_settings(self, *args):
        loc_arr = [self.location, self.def_location]
        unit = self.unit
        w = rw()
        w.write(loc_arr, unit)
        print("Current data saved.")


'''The main app class. This is the core of the whole application'''


# main app class
class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.material_style = "M3"
        return MainScreen()


if __name__ == "__main__":
    MainApp().run()
