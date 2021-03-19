import os
import requests
from urllib.parse import urlencode
import logging
from thespian.actors import *
from WeatherDatum import *
from NASADatum import *
class FetchWeatherDatum():
    def __init__(self):
        pass

class FetchNASADatum():
    def __init__(self):
        pass
class InitializeAPIActor():
    def __init__(self, dbActorRef, location, api_key):
        self.dbActorRef = dbActorRef
        self.location = location
        self.api_key = api_key

class WeatherAPIActor(Actor):

    def receiveMessage(self, msg, sender):
    
        #sets the API-key plus the longitude and latitude for location
        if isinstance(msg, InitializeAPIActor):
           self.dbActorRef = msg.dbActorRef
           self.location   = msg.location
           self.api_key    = msg.api_key
           try:
               self.lat, self.lon = self.get_city_lonlat()
               self.send(sender,True)
           except:
               self.send(sender,False)
        
        # ingests weather data and sends to database actor 
        elif isinstance(msg,FetchWeatherDatum):
           weatherDatum = self.get_current_datum()
           self.send(self.dbActorRef,weatherDatum)

        # ingests nasa data and sends to database actor 
        elif isinstance(msg,FetchNASADatum):
           nasa_data = self.get_nasa_data()
           self.send(self.dbActorRef,nasa_data)

    #retrieves: data (irradiation) from NASA API and return list of NASADatum
    def get_nasa_data(self):
        req_data = {"request":"execute",
                    "identifier":"SinglePoint",
                    "parameters":"SI_EF_TILTED_SURFACE",
                    "userCommunity":"SSE",
                    "tempAverage":"CLIMATOLOGY",
                    "outputList":"JSON",
                    "lat":self.lat, "lon":self.lon}
        base_url = "https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py"
        url      = base_url + '?' +urlencode(req_data)
        logging.info("""Retrieving irradiation for location: {0}""".format(self.location))
        response = requests.get(url,timeout=10)
        if (response.status_code == 200):
            logging.info("""Succesfull retrieved data for location: {0}""".format(self.location))
            data = response.json()

            irradiation = data['features'] \
                              [0]['properties'] \
                              ['parameter'] \
                              ['SI_EF_TILTED_SURFACE_LATITUDE']
            nasa_data = [NASADatum(irr, self.location, i) for i,irr in enumerate(irradiation)]
            return nasa_data
        else:
            logging.warning("""Unable to NASA data for location: {0}""".format(self.location))
         

    #retrieves: data (temperature, time, uvindex) from API and return WeatherDatum
    def get_current_datum(self):
        req_data = {'lat': self.lat, 'lon': self.lon, 'appid': self.api_key,'exclude':'minutely,hourly,daily,alerts' }
        base_url = "https://api.openweathermap.org/data/2.5/onecall" 
        url      = base_url + '?' +urlencode(req_data)
        logging.info("""Retrieving data for location: {0}""".format(self.location))
        response = requests.get(url,timeout=1)
        if (response.status_code == 200):
            logging.info("""Succesfull retrieved data for location: {0}""".format(self.location))
            data = response.json()
            return WeatherDatum(
                     temp=data['current']['temp'],
                     time=data['current']['dt']+data['timezone_offset'],
                     uvi=data['current']['uvi'],
                     location=self.location)
        else:
            logging.warning("""Unable to retrieve data for location: {0}""".format(self.location))

    #retrieves longitude and latitude from API and returns them
    def get_city_lonlat(self):
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        req_data = {'q': self.location, 'appid': self.api_key, 'exclude':'minutely,hourly,daily,alerts'}
        url      = base_url + '?' +urlencode(req_data)
        response = requests.get(url, timeout=1)
        data = response.json()
        if (response.status_code == 200):
            data = response.json()
            lat, lon = data['coord']['lat'], data['coord']['lon']
            logging.info("""Succesfully retrieved lon,lat ({0},{1}) for location: {2}""".format(lon, lat, self.location))
            return lat,lon 
        else:
            logging.warning("""Unable to retrieve lon,lat for location: {0};""".format(self.location))
