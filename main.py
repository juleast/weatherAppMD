# kivymd imports
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
# kivy imports
import kivy
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import FallOutTransition, RiseInTransition

# local imports
from apicall import weatherData, getLoc

kivy.require('2.1.0')

# load the kv files
Builder.load_file('weather.kv')
Builder.load_file('dialogcontents.kv')

# variables for special characters and units
units = {'metric': ["°C", "km/h"], 'us': ["°F", "mph"]}
degree = "°"
unit_change = [False]


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
        self.weather_error = MDDialog(
            type="custom",
            content_cls=ErrorContent(),
            buttons=[
                MDRaisedButton(
                    text="OK",
                    size_hint_x=1,
                    on_release=lambda x: self.weather_error.dismiss()
                )
            ]
        )
        #self.update()

    # function that updates what is displayed on the screen
    def show(self, unit, data):
        self.city_name.title = data['location']
        # main weather data values are updated here
        self.temp.text = f"{data['main'][0]}{units[unit][0]}"
        self.temp_feels.text = f"Feels like {data['main'][1]}{degree}"
        self.temp_low.text = f"{data['main'][2]}{degree}"
        self.temp_high.text = f"{data['main'][3]}{degree}"
        self.weather_condition.text = data['main'][4]
        self.weather_icon.source = f"./assets/icons/{data['main'][5]}.png"
        # misc weather data values are updated here
        self.weather_precip.text = f"{data['misc'][0]}%"
        self.weather_wind.text = f"{data['misc'][1]} {units[unit][1]}"
        self.weather_humid.text = f"{data['misc'][2]}%"

    def update(self):
        weather = weatherData(self.default, "c").now_fetch()
        weatherData(self.default, "c").tmr_fetch()
        if weather != -1:
            self.show("metric", weather)
        else:
            self.weather_error.open()

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
        test = self.picker.content_cls.location.text.split(",")
        if self.picker.content_cls.location.text != "" and len(test) == 2:
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
