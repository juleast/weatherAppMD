# importing libraries required to request API call from weather service
import requests as req
from datetime import datetime
from datetime import timedelta
from math import trunc
# api key from openweathermap
api_keys = ["6Q4JUN7Y8TYWPAE9SDJ59V6V6", "LQFCHSKEJDLP43RMKJW4G53XJ"]
# the base url for the weather service
base_urls = ["https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline", "https://freegeoip.live/json"]
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

    # function that will fetch the weather data from the api call
    def now_fetch(self):
        # get current time
        today = datetime.now()
        now = today.strftime("%Y-%m-%dT%H:%M:%S")
        print(now)
        # the final url is built into the url variable
        base = f"{base_urls[0]}/{self.city}/{now}?"
        url_options = f"unitGroup={temp_units[self.offset]}&key={api_keys[1]}&iconSet=icons2&include=current"
        url = f"{base}{url_options}"
        # this sends a get request with our url as the parameter
        r = req.get(url)
        # store the fetched json data
        data = r.json()

        # the cod key contains a status code, this conditional will check for a valid one in case of errors
        if data['queryCost'] == 1:
            print(data)
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
            return {'main': main, 'misc': misc}
        else:
            print("An error has occurred in weather fetching")
            return -1

    # function that will fetch weather data 1 day from current day
    def tmr_fetch(self):
        tmr_date = datetime.today() + timedelta(days=1)
        tmr = tmr_date.strftime("%Y-%m-%d")
        print(tmr)


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

