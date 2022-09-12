# kivymd imports
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
# kivy imports
import kivy
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import OptionProperty
from kivy.uix.screenmanager import FallOutTransition, RiseInTransition

# local imports
from tools.apicall import weatherData
from tools.check import internet

kivy.require('2.1.0')
# white background color
Window.clearcolor = (1, 1, 1, 1)

# load the kv files
Builder.load_file('weather.kv')
Builder.load_file('dialogcontents.kv')

# variables for special characters and units
units = {'metric': ["°C", "km/h"], 'us': ["°F", "mph"]}
degree = "°"
unit_change = [False]


# dialog class to add an option to change button direction
class Dialog(MDDialog):

    button_direction = OptionProperty(
        "right", options=["left", "right", "center"]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ids.root_button_box.anchor_x = self.button_direction


# widget for location changer popup
class PickerContent(MDBoxLayout):
    pass


# widget for error message popup
class ErrorContent(MDBoxLayout):
    pass


class MainScreen(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default = "Newmarket,Ontario"
        self.prev = ""
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
            ]
        )
        # popup dialog to show error message
        self.weather_error = Dialog(
            type="custom",
            content_cls=ErrorContent(),
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.weather_error.dismiss()
                )
            ],
            button_direction="center",
        )
        self.update()

    # function that updates today weather screen
    def today(self, unit, data):
        self.city_name.title = data['location']
        # main today weather data values are updated here
        self.temp.text = f"{data['main'][0]}{units[unit][0]}"
        self.temp_feels.text = f"Feels like {data['main'][1]}{degree}"
        self.temp_low.text = f"{data['main'][2]}{degree}"
        self.temp_high.text = f"{data['main'][3]}{degree}"
        self.weather_condition.text = data['main'][4]
        self.weather_icon.source = f"./assets/icons/{data['main'][5]}.png"
        # misc today weather data values are updated here
        self.weather_precip.text = f"{data['misc'][0]}%"
        self.weather_wind.text = f"{data['misc'][1]} {units[unit][1]}"
        self.weather_humid.text = f"{data['misc'][2]}%"

    # function that updates tmr weather screen
    def tmr(self, unit, data):
        # main tmr weather data values are updated here
        self.temp_low_tm.text = f"{data['main'][0]}{degree}"
        self.temp_high.text = f"{data['main'][1]}{degree}"
        self.weather_condition.text = data['main'][2]
        self.weather_icon.source = f"./assets/icons/{data['main'][3]}.png"
        # misc today weather data values are updated here
        self.weather_precip.text = f"{data['misc'][0]}%"
        self.weather_wind.text = f"{data['misc'][1]} {units[unit][1]}"
        self.weather_humid.text = f"{data['misc'][2]}%"

    def update(self):
        weather = weatherData(self.default, "c").now_fetch()
        weatherData(self.default, "c").tmr_fetch()
        # check if a valid weather data has been returned
        if weather != -1:
            self.today("metric", weather)
        else:
            self.weather_error.open()
            # check if there is a valid internet and switch back to last known good location
            if internet().check():
                self.default = self.prev

    # clears text
    def clear_text(self, *args):
        self.picker.content_cls.location.text = ""

    # method to close location switcher popup
    def cancel(self):
        self.picker.dismiss()
        self.picker.content_cls.location.helper_text = "Field cannot be left blank"
        Clock.schedule_once(self.clear_text, .15)

    # method that switches current weather location
    def save(self):
        # makes sure that user has entered in (city,region) format
        test = self.picker.content_cls.location.text.split(",")
        if self.picker.content_cls.location.text != "" and len(test) == 2:
            # backups current city name to revert when errors occur
            self.prev = self.default
            self.default = self.picker.content_cls.location.text
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
