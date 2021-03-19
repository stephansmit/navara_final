class NASADatum:
    def __init__(self,irradiation,location,time):
        self.irradiation =  irradiation
        self.location = location
        self.time=time
   
    def to_json(self):
       return  {
            "measurement": "irradiation",
            "time": self.time,
            "tags":{
                "location": self.location,
             },
            "fields": {
                "irradiation": float(self.irradiation),
            }
        }
