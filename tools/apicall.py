# importing libraries required to request API call from weather service
import requests as req
from datetime import datetime
from datetime import timedelta
from math import trunc

# api key from openweathermap
api_keys = ["6Q4JUN7Y8TYWPAE9SDJ59V6V6", "LQFCHSKEJDLP43RMKJW4G53XJ"]
# the base url for the weather service
base_urls = ["https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline",
             "https://freegeoip.live/json"]
# units dictionary
temp_units = {"c": "metric", "f": "us"}


# function that rounds given value and returns it as a string
def str_r(value):
    # checks if a given value has invalid data
    if value is not None:
        result = round(value)
        return str(result)
    # defaults any NoneType data to string 0
    else:
        return "0"


class weatherData:
    def __init__(self, city, offset):
        self.city = city
        self.offset = offset
        self.base = f"{base_urls[0]}/{self.city}"

    # function that will fetch the weather data from the api call
    def now_fetch(self):
        # get current time
        today = datetime.now()
        now = today.strftime("%Y-%m-%dT%H:%M:%S")
        # the URL to be fetched is divided into sections then built into the url variable
        base = f"{self.base}/{now}?"
        url_options = f"unitGroup={temp_units[self.offset]}&key={api_keys[0]}&iconSet=icons2&include=current"
        url = f"{base}{url_options}"
        # sends a get request to given url
        r = req.get(url)
        print(r.status_code)
        # check what status code the requested URL returns to determine if a valid data has been returned
        if r.status_code == 200:
            # store the fetched json data
            data = r.json()
            print(data)
            # get resolved address
            get_city = data['resolvedAddress'].split(",")
            if len(get_city) > 1 and get_city[0] == self.city.split(",")[0]:
                city = f"{get_city[0]},{get_city[1]}"
            else:
                city = self.city
            # variable to store current weather data
            data_now = data['currentConditions']
            # variable to store daily weather data
            data_d = data['days'][0]
            # main weather data
            temp = str_r(data_now['temp'])
            feels_like = str_r(data_now['feelslike'])
            min_temp = str_r(data_d['tempmin'])
            max_temp = str_r(data_d['tempmax'])
            descr = data_now['conditions'].title()
            icon = data_now['icon']
            # misc weather data
            precip = str_r(data_now['precipprob'])
            windspeed = str_r(data_now['windspeed'])
            humidity = str_r(data_now['humidity'])
            # store collected data
            main = [temp, feels_like, min_temp, max_temp, descr, icon]
            misc = [precip, windspeed, humidity]
            # return all acquired data as a dictionary
            return {'main': main, 'misc': misc, 'location': city}
        else:
            print("An error has occurred in fetching weather data")
            return -1

    # function that will fetch weather data 1 day from current day
    def tmr_fetch(self):
        tmr_date = datetime.today() + timedelta(days=1)
        tmr = tmr_date.strftime("%Y-%m-%d")
        # the URL to be fetched is divided into sections then built into the url variable
        base = f"{self.base}/{tmr}?"
        url_options = f"unitGroup={temp_units[self.offset]}&key={api_keys[0]}&iconSet=icons2"
        url = f"{base}{url_options}"
        # sends a get request to given url
        r = req.get(url)
        if r.status_code == 200:
            data = r.json()
            print(data)
            # variable to store daily weather data
            data_d = data['days'][0]
            # main weather data
            min_temp = str_r(data_d['tempmin'])
            max_temp = str_r(data_d['tempmax'])
            descr = data_d['conditions'].title()
            icon = data_d['icon']
            print(min_temp, max_temp, descr, icon)
        else:
            print("An error has occurred in fetching weather data for tmr")


# class that gets the current location of the device based on the IP address
class getLoc:
    def __init__(self):
        pass

    def fetch(self):
        url = f"{base_urls[1]}"
        r = req.get(url)
        data = r.json()
        if data['metro_code'] == 0:
            city = data['city']
            region = data['region_name']

            print(city, region)
            return f"{city}, {region}"
        else:
            print("An error has occurred in geoloc fetching")
            return -1