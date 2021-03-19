import pykka
import logging
from influxdb import InfluxDBClient
from WeatherDatum import *
from time import sleep


ConnectToDatabase = object()

class InfluxDBActor(pykka.ThreadingActor):
    def __init__(self, host='0.0.0.0', port=8086):
        super().__init__()
        self.host = host
        self.port = port
        self.data = []
        self.nmax = 4

    def on_stop(self):
        if self.data:
            self.write_to_influx()
        self.client.close()
        
    def on_receive(self, datum):
        if isinstance(datum,WeatherDatum):
           self.data.append(datum)
           if len(self.data) == self.nmax:
              self.write_to_influx()
        elif ConnectToDatabase:
            return self.connect_to_database()

    # connect to the influxdb 
    def connect_to_database(self):
        try:
            logging.info("""trying to connect to database at {0} with port {1}""".format(self.host,self.port))
            self.client = InfluxDBClient(host=self.host, port=self.port)
            self.client.create_database("dashboard") 
            self.client.switch_database("dashboard")
            logging.info("""succesfully connected to database""")
            return True
        except:
            logging.warning("""failed to connect to database at {0} with port {1}""".format(self.host, self.port))
            return False
    
    # write to influx database
    def write_to_influx(self):
        logging.info("writing data to influxdb")
        json = [d.to_json() for d in self.data]
        self.client.write_points(json)
        self.data = []
        logging.info("succesfull written to influxdb")
 
