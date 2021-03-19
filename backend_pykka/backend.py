import os
import pykka
import sys
import logging
from time import sleep
from InfluxDBActor import InfluxDBActor, ConnectToDatabase
from WeatherAPIActor import WeatherAPIActor, FetchWeatherDatum
logging.basicConfig(level=logging.DEBUG)

          
if __name__=="__main__":
    
    # start InfluxDBActor
    logging.info("starting InfluxDBActor")
    influxActorRef = InfluxDBActor.start()
    
    # exit when can't connect to database
    if not influxActorRef.ask(ConnectToDatabase):
        influxActorRef.stop()
        sys.exit()
    
    # hardcoded locations FTTB
    locations =[
    "Utrecht",
    "Madrid",
    "Val Thorens",
    "London",
    "Stockholm"
    ]

    # start WeatherAPIActors for each location
    logging.info("starting weatherAPIActors")
    weatherActorsRef = [WeatherAPIActor.start(influxActorRef, loc) for loc in locations]

    # Fetching data every 60 seconds
    sleep(0.01)
    while True:
       try: 
           if not any([ref.is_alive() for ref in weatherActorsRef]):
               logging.warning("all the WeatherAPIActors to are dead; stop the influxDBActor and quit")
               influxActorRef.stop()
               sys.exit()
           
           logging.info("tell all the WeatherAPIActors to start fetching a datum")
           for ref in weatherActorsRef:
               if ref.is_alive():
                  ref.tell(FetchWeatherDatum)
           sleep(60)
       except KeyboardInterrupt:
             logging.info("interrupting with keyboard")
             pykka.ActorRegistry.stop_all()
             sys.exit()
