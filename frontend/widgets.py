import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from app import app 
import datetime
from staticDataBoard import *

def create_widget_div(widget, title, id_name):
    return html.Div([
                    html.Div([
                      html.H6(title,
                      style={'padding': '1em'})
                      ],
                    ), widget
                    ], id=id_name)


#--------------------cities
#city dropdown
cityDropDown = dcc.Dropdown(
        id='cityDropdown',
        options=[{'label': i, 'value':i} for i in df_cities.index.values],
        value=df_cities.index.values[0],
        clearable=False,
)
#area slider
areaSlider = dcc.Slider(
    id='areaSlider',
    min=1,
    max=df_cities.iloc[0]['capacity'],
    value=df_cities.iloc[0]['capacity']/2.0,
    tooltip={'always_visible':True}
)
#area price slider
areaPriceSlider = dcc.Slider(
    id='areaPriceSlider',
    min=0,
    max=3500,
    value=df_cities.iloc[0]['plot_price']/df_cities.iloc[0]['capacity'],
    tooltip={'always_visible':True}
)
#elec price slider
elecPriceSlider = dcc.Slider(
    id='elecPriceSlider',
    min=5,
    max=25,
    value=df_cities.iloc[0]['electricity_price'],
    tooltip={'always_visible':True}
)

#----------------- solar panels
#solar efficiency slider
spEffSlider = dcc.Slider(
    id='spEffSlider',
    min=5,
    max=40,
    value=df_solar.iloc[0]['efficiency'],
    tooltip={'always_visible':True}
)
#solar heat coefficient slider
spHcSlider = dcc.Slider(
    id='spHcSlider',
    min=5,
    max=40,
    value=df_solar.iloc[0]['heat_coefficient'],
    tooltip={'always_visible':True}
)
#module price slider
spPriceSlider = dcc.Slider(
    id='spPriceSlider',
    min=50,
    max=300,
    value=df_solar.iloc[0]['price'],
    tooltip={'always_visible':True}
)
#type radio
typeRadio = dcc.RadioItems(
    id= 'typeRadio',
    options=[{'label':i, 'value':i} for i in df_solar.index.values],
    value=df_solar.index.values[0],
    labelStyle={'margin-right': '1em'},
    style={'margin-left':'1em'}
)



#------------------- system performance slider
performanceSlider = dcc.Slider(
    id='performanceSlider',
    min=50,
    max=100,
    value=75,
    tooltip={'always_visible':True}
)



cityDiv = create_widget_div(cityDropDown, "Select the city", 'cityDiv')
areaPriceDiv = create_widget_div(areaPriceSlider, "Select price of land area [euro/m^2]", 'areaPriceDiv')
elecPriceDiv = create_widget_div(elecPriceSlider, "Select price of electricy [eurocent/kWh]", 'elecPriceDiv')
areaDiv = create_widget_div(areaSlider, "Select solar panel area [m^2]", 'areaDiv')

spPriceDiv = create_widget_div(spPriceSlider, "Select price of solar modules [euro/m^2]", 'spPriceDiv')
spEffDiv = create_widget_div(spEffSlider, "Select efficiency of solar modules [%]", 'spEffDiv')
spHcDiv = create_widget_div(spHcSlider, "Select the heat coefficient of solar modules [%]", 'spHcDiv')
typeDiv = create_widget_div(typeRadio, "Select type of solar panel", 'typeDiv')

performanceDiv = create_widget_div(performanceSlider, "Select the system performance coefficient [%]",'performanceDiv')

# resets the min and max of area to location specific and the land price to the default
@app.callback(
    [Output('areaSlider', 'max'),
     Output('areaSlider', 'marks'),
     Output('areaSlider', 'value'),
     Output('areaPriceSlider', 'value'),
     Output('elecPriceSlider', 'value'),
     Output('spPriceSlider', 'value'),
     Output('spEffSlider', 'value'),
     Output('spHcSlider', 'value')] ,
   [Input('cityDropdown', 'value'),
    Input('typeRadio', 'value')]
)
def update_citySliders(location, sp_type):
    ctx = dash.callback_context

    wid = ctx.triggered[0]['prop_id'].split('.')[0]

    if (wid=='cityDropdown'):
       elec_price, area, plot_price, area_price = get_city_default_values(location)
       area_max = area
       area_value = area
       area_marks = {0: '0 m^2', 
                int(area/2): str(int(area/2)) + ' m^2',
                int(area): str(int(area))+' m^2'}
       return area_max, area_marks,area_value, area_price, elec_price, dash.no_update,dash.no_update,dash.no_update
    elif (wid=='typeRadio'):
       eff, hc, sp_price = get_sp_default_values(sp_type)
       return dash.no_update, dash.no_update, dash.no_update,dash.no_update, dash.no_update, sp_price, eff, hc
    else:
       elec_price, area, plot_price, area_price = get_city_default_values(location)
       area_max = area
       area_value = area
       area_marks = {0: '0 m^2', 
                int(area/2): str(int(area/2)) + ' m^2',
                int(area): str(int(area))+' m^2'}
       eff, hc, sp_price = get_sp_default_values(sp_type)
       return area_max, area_marks, area_value,area_price, elec_price, sp_price, eff, hc

#widgets
widgetCol = dbc.Col([html.H4('Parameters', style={"padding":"1em"}),
    cityDiv,areaDiv, spEffDiv, spHcDiv,areaPriceDiv, elecPriceDiv, spPriceDiv, performanceDiv
    ,typeDiv],
    width=4, style={'margin-left': '4em'}) 
