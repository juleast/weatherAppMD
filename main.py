# kivymd imports
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
# kivy imports
import kivy
kivy.require('2.1.0')
from kivy.lang import Builder
from kivy.config import Config
# local imports
from apicall import weatherData, getLoc


# load the main kvlang file
Builder.load_file('weather.kv')

# variables for special characters and units
units = {'metric': ["°C", "km/h"], 'us': ["°F", "mph"]}
degree = "°"
unit_change = [False]

# get an initial detected location
default = "Newmarket,Ontario"


class mainScreen(MDBoxLayout):
    # function that updates what is displayed on the screen
    def show(self, unit, city, data):
        self.city_name.title = city
        # main weather data values are updated here
        self.temp.text = f"{data['main'][0]} {units[unit][0]}"
        self.temp_feels.text = f"Feels like {data['main'][1]}{degree}"
        self.temp_low.text = f"Low {data['main'][2]}{degree}"
        self.temp_high.text = f"High {data['main'][3]}{degree}"
        self.weather_condition.text = data['main'][4]
        # misc weather data values are updated here
        self.weather_precip.text = f"{data['misc'][0]}%"
        self.weather_wind.text = f"{data['misc'][1]}{units[unit][1]}"
        self.weather_humid.text = f"{data['misc'][2]}%"
        self.weather_icon.source = "./assets/icons/weather_night.png"

    def update(self):
        weather = weatherData(default, "c").fetch()
        if weather != -1:
            self.show("metric", default, weather)


class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "LightBlue"
        return mainScreen()


if __name__ == "__main__":
    MainApp().run()
