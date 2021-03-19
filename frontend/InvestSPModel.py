from influxdb import InfluxDBClient
from datetime import datetime
import calendar
import numpy  as np
import pandas as pd

def get_df_w_year(df,y):
    df['year']=y
    return df

class InvestSPModel():
    def __init__(self, locations):
       self.client = InfluxDBClient(host='localhost', port=8086)
       self.client.switch_database('dashboard')
       self.df_nasa = pd.concat([ self.get_nasa_data(l) for l in locations])
       self.df_total = self.set_total_table(self.df_nasa)
    
    # get the irradiation for a location per month 
    def get_nasa_data(self,location):
       tables = self.client.query("""SELECT * from irradiation where location='{0}' ORDER BY time ASC Limit 12""".format(location))
       data = [(i+1,p['irradiation'], p['location']) for i,p in enumerate(tables.get_points())]
       df = pd.DataFrame(data,columns=['month_nr', 'irradiance_m2', 'location'])
       df['month']= df['month_nr'].apply(lambda x:calendar.month_name[x])
       return df

    # add the months, years, number of day, power wo losses per m^2 each month
    def set_total_table(self,df):
       years = np.arange(2021,2036)
       dfs = [df.copy() for y in years]
       dfs = [get_df_w_year(df,y) for y,df in zip(years,dfs)]
       df = pd.concat(dfs)
       df['month']= df['month_nr'].apply(lambda x:calendar.month_name[x])
       df['days'] = df.apply(lambda x: calendar.monthrange(x['year'] , x['month_nr'])[1],axis=1)
       df['irradiance_m2_month'] = df['days']*df['irradiance_m2'] 
       df['date'] = df.apply(lambda x: datetime(month = x['month_nr'], year=x['year'], day=1), axis=1)
       return df

    # set location, calculate the power production and the revenu
    def set_location(self,location, performance, efficiency, area, elec_price, land_price, sp_price):
       today = datetime.today()
       self.df_total['filter'] = self.df_total.apply(lambda x: 
                              ((x['year']==2021 and 
                              x['month_nr']>today.month) or 
                              x['year']>2021) and 
                              x['location']==location, axis=1)
       self.df = self.df_total[self.df_total['filter']].copy()
       self.calc_performance(performance, efficiency, area, elec_price, land_price, sp_price)

    # calculate the power production and the revenue
    def calc_performance(self, performance, efficiency, area, elec_price, land_price, sp_price):
       self.df['power']   = self.df['irradiance_m2_month']*(performance/100.)*(efficiency/100.)*area
       self.calc_revenue_profit(elec_price,land_price, sp_price, area)
    
    # calculate the revenue 
    def calc_revenue_profit(self, elec_price, land_price, sp_price, area):
       self.df['revenue'] = self.df['power']*elec_price/100.
       self.df['invest_costs']=self.calc_invest_costs(sp_price, land_price, area)
       self.df.sort_values(['year','month_nr'], inplace=True)
       self.df['cumrevenue'] = self.df['revenue'].cumsum()
       self.df['profit'] = -self.df['invest_costs']+self.df['cumrevenue']
       self.df['loss'] = self.df['profit'].apply(lambda x: 'Net loss' if x<0 else 'Net profit')

    # calculate investment costs
    def calc_invest_costs(self, sp_price, land_price,area):
       return (sp_price + land_price)*area

    # get yearly revenue and power
    def get_yearly_df(self):
        return self.df.groupby('year')[['revenue', 'power']].sum()
