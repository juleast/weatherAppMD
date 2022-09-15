# kivymd imports
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

# local imports
from tools.apicall import weatherData
from tools.check import internet
from threading import Thread

# some misc options
Loader.loading_image = "./assets/images/bg/25501.jpg"
require('2.1.0')

# load the kv files
Builder.load_file('weather.kv')
Builder.load_file('dialogcontents.kv')

# variables for special characters and units
units = {'metric': ["°C", "km/h", "c"], 'us': ["°F", "mph", "f"]}
degree = "°"
unit_change = [False]


# dialog class to add an option to change button direction
class MDDialog(MDDialog):

    button_direction = OptionProperty(
        "right", options=["left", "right", "center"]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ids.root_button_box.anchor_x = self.button_direction


# widget for location changer popup
class PickerContent(MDBoxLayout):
    pass


# widget for fetch error message popup
class ErrorContent(MDBoxLayout):
    pass


# widget for internet error popup
class ConErrorContent(MDBoxLayout):
    pass


# the main screen widget
class MainScreen(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # initial required variables for weather data
        self.location = "Newmarket,Ontario"
        self.unit = "metric"
        self.prev = ""
        # a thread to run the update function as to not interfere with the main app process
        # popup dialog for changing locations
        self.picker = MDDialog(
            title="Change location",
            type="custom",
            content_cls=PickerContent(),
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.cancel()
                ),
                MDRaisedButton(
                    text="SAVE",
                    on_release=lambda x: self.save()
                )
            ],
        )
        # popup dialog to show error message
        self.weather_error = MDDialog(
            type="custom",
            content_cls=ErrorContent(),
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.weather_error.dismiss()
                )
            ],
            button_direction="center",
        )
        # popup dialog to show internet error message
        self.internet_error = MDDialog(
            type="custom",
            content_cls=ConErrorContent(),
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.internet_error.dismiss()
                )
            ],
            button_direction="center",
        )
        Clock.schedule_once(self.get_update, 3)

    def get_update(self, *args):
        Thread(target=self.update, args=(), daemon=True).start()

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
        self.ids.weather_icon.reload()
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

    # the main update method for screen
    @mainthread
    def update(self, *args):
        if internet().check():
            weather_today = weatherData(self.location, units[self.unit][2]).now_fetch()
            weather_tmr = weatherData(self.location, units[self.unit][2]).tmr_fetch()
            # check if a valid weather data has been returned
            if weather_today != -1 and weather_tmr != 1:
                self.today(self.unit, weather_today)
                self.tmr(self.unit, weather_tmr)
            else:
                self.weather_error.open()
                self.location = self.prev
        else:
            print("Could not verify a valid internet connection")
            Clock.schedule_once(self.internet_error.open, 1)

    # clears text
    def clear_text(self, *args):
        self.picker.content_cls.location.text = ""

    # method to close location switcher popup
    def cancel(self):
        self.picker.dismiss()
        self.picker.content_cls.location.helper_text = "Field cannot be left blank"
        Clock.schedule_once(self.clear_text, .15)

    # method that changes current weather location
    def save(self):
        # makes sure that user has entered in (city,region) format
        test = self.picker.content_cls.location.text.split(",")
        if self.picker.content_cls.location.text != "" and len(test) == 2:
            # backups current city name to revert when errors occur
            self.prev = self.location
            self.location = self.picker.content_cls.location.text
            self.picker.content_cls.location.text = ""
            self.picker.dismiss()
            self.picker.content_cls.location.helper_text = "Field cannot be left blank"
            Clock.schedule_once(self.clear_text, .15)
            self.nav_drawer.set_state("close")
            self.update()
        else:
            self.picker.content_cls.location.helper_text = "Must be (city,region) format"
            self.picker.content_cls.location.error = True

    # method that switches to settings screen
    def open_settings(self):
        self.ids.screenmanager.transition = RiseInTransition(duration=0.2)
        self.ids.screenmanager.current = 'settings'
        self.nav_drawer.set_state("close")

    # method that switches to main screen
    def open_main(self):
        self.ids.screenmanager.transition = FallOutTransition(duration=0.2)
        self.ids.screenmanager.current = "main"


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
