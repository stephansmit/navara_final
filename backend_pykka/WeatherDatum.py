class WeatherDatum:
    def __init__(self,temp,uvi,location,time):
        self.temp = temp
        self.location = location
        self.time = time
        self.uvi = uvi

    def convert_to_time(time):
        return "2009-11-10T23:00:00Z"
   
    def to_json(self):
       return  {
            "measurement": "weatherdata",
            "time": self.convert_to_time(self.time),
            "tags":{
                "location": self.location,
             },
            "fields": {
                "temp": self.temp,
                "uvi": self.uvi,
            }
        }
