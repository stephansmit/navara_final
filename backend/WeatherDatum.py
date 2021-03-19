from datetime import datetime
class WeatherDatum:
    def __init__(self,temp,uvi,location,time):
        self.temp = temp
        self.location = location
        self.time = time
        self.uvi = uvi

    def get_time(self):
        return datetime.utcfromtimestamp(self.time).strftime('%Y-%m-%dT%H:%M:%SZ')
   
    def to_json(self):
       return  {
            "measurement": "weatherdata",
            "time": self.get_time(),
            "tags":{
                "location": self.location,
             },
            "fields": {
                "temp": float(self.temp),
                "uvi": float(self.uvi),
            }
        }
