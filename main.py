# kivymd imports
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
# kivy imports
import kivy

kivy.require('2.1.0')
from kivy.lang import Builder
# local imports
from apicall import weatherData, getLoc

# load the main kvlang file
Builder.load_file('weather.kv')

# variables for special characters and units
units = {'metric': ["°C", "km/h"], 'us': ["°F", "mph"]}
degree = "°"
unit_change = [False]

# get an initial detected location
default = getLoc().fetch()


class MainScreen(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.update()

    # function that updates what is displayed on the screen
    def show(self, unit, city, data):
        self.city_name.title = city
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
        weather = weatherData(default, "c").now_fetch()
        weatherData(default, "c").tmr_fetch()
        if weather != -1:
            self.show("metric", default, weather)


class Content(MDBoxLayout):
    pass


class MainApp(MDApp):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.picker = None
        self.picker = MDDialog(
            title="Change location",
            content_clse=Content(),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.picker.dismiss()
                ),
                MDRaisedButton(
                    text="SAVE"
                )
            ]
        )

    def build(self):
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.material_style = "M3"
        return MainScreen()


if __name__ == "__main__":
    MainApp().run()
