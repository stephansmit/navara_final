import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
from app import app


static_data = pd.read_excel("static_set.xlsx", sheet_name=['Cities','Solar panels'])
df_solar = static_data['Solar panels'].set_index("type")
df_cities = static_data['Cities'].set_index('city')
df_solar_table = static_data['Solar panels'].drop('square_meter',axis=1) \
                                            .rename({"efficiency": "Efficiency (%)",
                                                     "type": "Type",
                                                     "heat_coefficient":"Heat Coefficient",
                                                     "price": "Price (Euro/m^2)"}
                                                    ,axis=1)
df_cities_table = static_data['Cities'].rename({"city": "City",
                                                "country": "Country",
                                                "capacity": "Capacity (m^2)",
                                                "plot_price": "Plot price (Euro)",
                                                "electricity_price": "Electricity Price (Euro)"}
                                               ,axis=1)
def get_city_default_values(location):
    elec_price    = df_cities.loc[location]['electricity_price']
    area  = df_cities.loc[location]['capacity']
    plot_price  = df_cities.loc[location]['plot_price']
    area_price = plot_price/area
    return elec_price, area, plot_price, area_price

def get_sp_default_values(sp_type):
    eff           = df_solar.loc[sp_type]['efficiency']
    hc    = df_solar.loc[sp_type]['heat_coefficient']
    sp_price = df_solar.loc[sp_type]['price']
    return eff, hc, sp_price
    
solar_table = dash_table.DataTable(
    id='solar-table',
    columns=[{"name": i, "id": i} for i in df_solar_table.columns],
    data=df_solar_table.to_dict('records'),
    style_table={'padding':"1em"}
)

#city table widget
city_table = dash_table.DataTable(
    id='city-table',
    columns=[{"name": i, "id": i} for i in df_cities_table.columns],
    data=df_cities_table.to_dict('records'),
    style_table={'padding':"1em"}
)



#static data html
staticDataBoardDiv= html.Div(
    [
        dbc.Row(
            [
                dbc.Col([solar_table, city_table], width=6)
            ]
        ),
    ]
)
