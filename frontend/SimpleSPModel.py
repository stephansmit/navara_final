from influxdb import InfluxDBClient
import pandas as pd
from datetime import datetime, timedelta



class SimpleSPModel():
    def __init__(self, location, area, hc, price, eff):
       self.hc = hc
       self.area = area
       self.price = price
       self.eff = eff
       self.location = location
       self.client = InfluxDBClient(host='localhost', port=8086)
       self.client.switch_database('dashboard')
       self.update_location(location)

    # get the mean hourly data for a location 
    def get_df_hourly(self):
        tables = self.client.query("""SELECT mean(*) from weatherdata 
                                      where location='{0}' and 
                                      time < now() and time > now() - 2d 
                                      group by time(1h) fill(linear)""".format(self.location))
        data = [(p['time'], p['mean_temp']-273, p['mean_uvi']) for p in tables.get_points() if p['mean_temp'] ]
        return pd.DataFrame(data,columns=['time','temp','uvi'])
    
    # get the current weather data for a location
    def get_df_current(self):
        tables = self.client.query("""SELECT * from weatherdata where location='{0}' ORDER BY time DESC Limit 1""".format(self.location))
        data = [(p['time'], p['temp']-273.15, p['uvi']) for p in tables.get_points()]
        return pd.DataFrame(data,columns=['time','temp','uvi'])

    # calculate the irradiance
    def calc_irradiance(self, df):
        df['datetime']       = df['time'].apply(lambda x:  datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))
        df['pwr_wo_loss_kwh']= df['uvi'].apply(lambda x: (x*104-18.365)/1000 if (x*104-18.365) > 0 else 0 )
        return df
     
    # calculate the solar power and irradiance including losses
    def calc_power(self,df):
        df['pwr_w_loss_kwh']= df.apply(lambda x: x['pwr_wo_loss_kwh']*(1-(self.hc/100)*(x['temp']-24)) 
                                                if x['temp']>24 else x['pwr_wo_loss_kwh'], axis=1)
        df['area']=self.area
        df['eff'] = self.eff
        df['solar_pwr']     = df.apply(lambda x: self.area*(self.eff/100)*x['pwr_w_loss_kwh'], axis=1)
        return df
    
    # update the location and hourly and current data 
    def update_location(self, location):
        self.location = location
        self.df_hourly = self.calc_power(self.calc_irradiance(self.get_df_hourly()))
        self.df_current = self.calc_power(self.calc_irradiance(self.get_df_current()))
    
    # update the hourly and current power data with the new parameters
    def update_parameter(self,area, hc, eff, elec_price):
        self.hc = hc
        self.area = area
        self.price = elec_price
        self.eff = eff
        self.df_hourly = self.calc_power(self.df_hourly)
        self.df_current = self.calc_power(self.df_current)

    def update_city(self,location, elec_price, area):
        self.area = area
        self.price = elec_price
        self.update_location(location)
    
    def update_sptype(self,eff, hc):
        self.eff = eff
        self.hc = hc
        self.df_hourly = self.calc_power(self.df_hourly)
        self.df_current = self.calc_power(self.df_current)

    # update all the data with the location and new parameters
    def update_all(self,location,area, hc, eff, elec_price):
        self.hc = hc
        self.area = area
        self.price = elec_price
        self.eff = eff
        self.update_location(location)

    # update the current weather data
    def update_current(self):
        self.df_current = self.calc_power(self.calc_irradiance(self.get_df_current()))

    # get the last 24 hours 
    def get_last_24(self):
        d= datetime.today() - timedelta(days=1)
        return self.df_hourly[self.df_hourly['datetime'] >= d].sum()

