# importing libraries required to request API call from weather service
import requests as req
from datetime import datetime
from math import trunc
# api key from openweathermap
api_keys = ["6Q4JUN7Y8TYWPAE9SDJ59V6V6", ""]
# the base url for the weather service
base_urls = ["https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/", "https://freegeoip.live/json"]
# units dictionary
temp_units = {"c": "metric", "f": "us"}


# function that rounds given value and returns it as a string
def str_r(value):
    result = round(value)
    return str(result)


class weatherData:
    def __init__(self, city, offset_type):
        self.city = city
        self.offset_type = offset_type

    # function that will fetch the weather data from the api call
    def fetch(self):
        # get current time
        today = datetime.now()
        now = today.strftime("%Y-%m-%dT%H:%M:%S")
        # the final url is built into the url variable
        url = f"{base_urls[0]}{self.city}/{now}?unitGroup={temp_units[self.offset_type]}&key={api_keys[0]}&include=current"
        # this sends a get request with our url as the parameter
        r = req.get(url)
        # store the json data fetched
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
            # misc weather data
            precip = str_r(data_now['precipprob'])
            windspeed = str_r(data_now['windspeed'])
            humidity = str_r(data_now['humidity'])
            # return all acquired data as a dictionary
            return {'main': [temp, feels_like, min_temp, max_temp, descr], 'misc': [precip, windspeed, humidity]}
        else:
            print("An error has occurred in weather fetching")
            return -1


class getLoc:
    def __init__(self):
        pass

    def fetch(self):
        url = f"{base_urls[1]}"
        r = req.get(url)
        data = r.json()
        print(data)
        if data['metro_code'] == 0:
            city = data['city']
            region = data['region_name']

            print(city, region)
            return [city, region]
        else:
            print("An error has occurred in geoloc fetching")
            return -1

