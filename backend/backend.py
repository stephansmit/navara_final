import os
import sys
import logging
from time import sleep
from InfluxDBActor import InfluxDBActor, InitializeDatabase, CloseDatabase
from WeatherAPIActor import WeatherAPIActor, FetchWeatherDatum, InitializeAPIActor, FetchNASADatum
logging.basicConfig(level=logging.DEBUG)
from thespian.actors import *

          
if __name__=="__main__":

    #load API key
    API_KEY = os.environ["API_KEY"]
    
    # hardcoded locations FTTB
    locations =[
    "Utrecht",
    "Madrid",
    "Val Thorens",
    "London",
    "Stockholm"
    ]


    logging.info("starting actor system")
    system = ActorSystem()

    logging.info("starting InfluxDBActor")
    influxActorRef = system.createActor(InfluxDBActor)
   
    # check if database is connected
    if not system.ask(influxActorRef,InitializeDatabase()):
        logging.warning("Doesnt connect to database; shutting down InfluxDBActor")
        system.tell(influxActorRef, ActorExitRequest())
        logging.warning("System exit")
        sys.exit()
    
    # start WeatherAPIActors for each location
    logging.info("starting weatherAPIActors")
    weatherActorsRef = [system.createActor(WeatherAPIActor) for i in locations]

    # initialize the WeatherAPIActors with the lon and lat
    initialize_objs = [InitializeAPIActor(influxActorRef, loc, API_KEY) for loc in locations]
    succes_initialized = [system.ask(ref,ini_obj) for ref, ini_obj in zip(weatherActorsRef,initialize_objs)]
    
    # kill actors than dont work gather working actors
    workingActorsRef = []
    for ref, succes in zip(weatherActorsRef,succes_initialized):
        if not succes:
            system.tell(ref, ActorExitRequest())
        else:
            workingActorsRef.append(ref)

    # if no actors left: close db, kill actor and exit
    if not workingActorsRef:
        logging.warning("no weatherAPIActors alive due to failed initialization")
        logging.info("closing database and kill database actor")
        system.tell(influxActorRef, CloseDatabase())
        system.tell(influxActorRef, ActorExitRequest())
        logging.warning("System exit")
        sys.exit()
    
    # fetch the nasa data
    for ref in workingActorsRef:
        system.tell(ref, FetchNASADatum())

    while True:
        # start fetching the data every 7.5 minutes
        try: 
            logging.info("tell all the WeatherAPIActors to start fetching a datum")
            for ref in workingActorsRef:
                system.tell(ref, FetchWeatherDatum())
            sleep(7.5*60)

        # if keyboard interrupt kill all actors
        except KeyboardInterrupt:
              logging.warning("interrupting with keyboard")
              system.shutdown()
              logging.warning("System exit")
              sys.exit()

