import logging
from influxdb import InfluxDBClient
from WeatherDatum import *
from NASADatum import NASADatum
from time import sleep
from thespian.actors import *

class InitializeDatabase:
    def __init__(self, host='localhost', port=8086):
        self.host = host
        self.port = port

class CloseDatabase:
    def __init__(self):
        pass

class InfluxDBActor(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nmax = 5
        self.data = []

    def receiveMessage(self, msg, sender):

        #write weatherdata to influxdb when 5 datapoints gathered
        if isinstance(msg,WeatherDatum):
           self.data.append(msg)
           if len(self.data) == self.nmax:
              self.write_to_influx()
        
        # initialize and connect to database
        elif isinstance(msg,InitializeDatabase):
            self.host = msg.host
            self.port = msg.port
            self.send(sender,self.connected_to_database())

        #write nasa data to influx
        elif isinstance(msg,list):
           self.write_nasa_to_influx(msg)

        # close the database
        elif isinstance(msg,CloseDatabase):
           self.client.close()
           logging.info("""Closed connection with database""")

    # connect to the database
    def connected_to_database(self):
        try:
           logging.info("""trying to connect to database at {0} with port {1}""".format(self.host,self.port))
           self.client = InfluxDBClient(host=self.host, port=self.port)
           self.client.create_database("dashboard") 
           self.client.switch_database("dashboard")
           logging.info("""succesfully connected to database""")
           return True
        except:
           logging.warning("""failed to connect to database at {0} with port {1}""".format(self.host,self.port))
           return False

    
    # write to influx database
    def write_to_influx(self):
        logging.info("writing data to influxdb")
        json = [d.to_json() for d in self.data]
        self.client.write_points(json)
        self.data = []
        logging.info("succesfull written to influxdb")
    
    def write_nasa_to_influx(self, nasa_data):
        logging.info("writing nasa data to influxdb")
        json = [d.to_json() for d in nasa_data]
        self.client.write_points(json)
        logging.info("succesfull written nasa data to influxdb")

