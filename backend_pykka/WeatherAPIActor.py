import pykka
import os
import requests
from urllib.parse import urlencode
import logging
from WeatherDatum import *

FetchWeatherDatum = object()
GetAPIInfo = object()
#api actor for each location
class WeatherAPIActor(pykka.ThreadingActor):
    def __init__(self, dbActorRef, location):
        super().__init__()
        self.dbActorRef = dbActorRef
        self.location = location
    
    #sets the API-key plus the longitude and latitude
    def on_start(self):
        self.api_key = os.environ['API_KEY']
        self.lat, self.lon = self.get_city_lonlat()
     
    #ingests data and sends to database actor 
    def on_receive(self,message):
        if message is FetchWeatherDatum:
           weatherDatum = self.get_current_datum()
           self.dbActorRef.tell(weatherDatum)

    #retrieves: data (temperature, time, uvindex) from API and return WeatherDatum
    def get_current_datum(self):
        req_data = {'lat': self.lat, 'lon': self.lon, 'appid': self.api_key }
        base_url = "https://api.openweathermap.org/data/2.5/onecall" 
        url = base_url + '?' +urlencode(req_data)
        logging.info("""Retrieving data for location: {0}""".format(location))
        response = requests.get(url,timeout=1)
        if (response.status_code == 200):
            logging.info("""Succesfull retrieved data for location: {0}""".format(location))
            data = response.json()
            return WeatherDatum(
                     temp=data['current']['temp'],
                     time=data['current']['dt'],
                     uvi=data['current']['uvi'],
                     location=self.location)
        else:
            logging.warning("""Unable to retrieve data for location: {0}""".format(location))

    #retrieves longitude and latitude from API
    def get_city_lonlat(self):
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        req_data = {'q': self.location, 'appid': self.api_key}
        url = base_url + '?' +urlencode(req_data)
        response = requests.get(url, timeout=1)
        data = response.json()
        if (response.status_code == 200):
            logging.info("""Succesfull retrieved lon,lat for location: {0}""".format(location))
            data = response.json()
            return data['coord']['lat'], data['coord']['lon']
        else:
            logging.warning("""Unable to retrieve lon,lat for location: {0}; shutting down Actor""".format(location))
            self.actor_ref.stop()
