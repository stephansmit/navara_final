import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from app import app
from widgets import *
from staticDataBoard import *
from SimpleSPModel import SimpleSPModel

def create_weather_chart(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]]) 
    fig.add_trace(
        go.Scatter(x=df['datetime'], y=df["temp"], name="Temperature") ,
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df['datetime'], y=df["uvi"], name="UV-index"),
        secondary_y=True,
    )
    fig['layout']['title'].update(text='Weather condition last 48 hours')
    fig['layout']['xaxis1'].update(title_text='Date')
    fig['layout']['yaxis1'].update(title_text='Temperature', title_font_color='blue')
    fig['layout']['yaxis2'].update(title_text='UV-index', title_font_color='red')

    return fig

def create_current_div(temp, uvi, power, power24, profit24, location):
    style = {'padding': '5px', 'fontSize': '20px', 'margin-left': '5em' }
    return [
        html.Div(html.Span(['Current Temperature [Celcius]: ',
                 html.Span('{0:.2f}'.format(temp),
                 style={'float':'right'})], style=style), 
                 style={'width':'40%'}),
        html.Div(html.Span(['Current UV-index  [-]: ',
                 html.Span('{0:.2f}'.format(uvi),         
                 style={'float':'right'})], style=style), 
                 style={'width':'40%'}),
        html.Div(html.Span(['Current Power [kW]: ',
                 html.Span('{0:.2f}'.format(power),           
                 style={'float':'right'})], style=style), 
                 style={'width':'40%'}),
        html.Div(html.Span(['Power produced 24 hours [kWh]: ',
                 html.Span('{0:.2f}'.format(power24),           
                 style={'float':'right'})], style=style), 
                 style={'width':'40%'}),
        html.Div(html.Span(['Revenue 24 hours [euro]: ',
                 html.Span('{0:.2f}'.format(profit24),           
                 style={'float':'right'})], style=style), 
                 style={'width':'40%'}),
        html.Div(html.Span(['Location: ',
                 html.Span('{0}'.format(sp.location),                  
                 style={'float':'right'})], style=style), style={'width':'40%'})
    ]

location = df_cities.index.values[0]
sp_type = df_solar.index.values[0]
elec_price, area, plot_price, area_price = get_city_default_values(location)
eff, hc, sp_price = get_sp_default_values(sp_type)
sp = SimpleSPModel(location, area, hc, elec_price, eff)

#current power graph
currentPower =  dcc.Graph(id="hourly-bar-chart")
currentWeather =  dcc.Graph(id="hourly-weather-chart")


#update bar charts in case of change of location 
@app.callback(
    [Output("hourly-bar-chart", "figure"), 
    Output("hourly-weather-chart", "figure"),
    Output('live-update-text', 'children')],
    [Input("cityDropdown", "value"),
     Input("typeRadio", "value"),
     Input("interval-component", "n_intervals"),
     Input('areaPriceSlider', 'value'),
     Input("elecPriceSlider", "value"),
     Input("areaSlider", "value"),
     Input("spEffSlider", "value"),
     Input("spHcSlider", "value")
      ])
def update_bar_chart_city(location,sp_type,n,area_price, elec_price, area, eff, hc):
    ctx = dash.callback_context
    wid = ctx.triggered[0]['prop_id'].split('.')[0]
    if (wid=='cityDropdown'):
       elec_price, area, plot_price, area_price = get_city_default_values(location)
       sp.update_city(location, elec_price, area)
    elif (wid=='typeRadio'):
       eff, hc, sp_price = get_sp_default_values(sp_type)
       sp.update_sptype(eff, hc)
    elif (wid=='interval-component'):
       sp.update_current()
    elif None:
       location=df_solar.index.values[0]
       elec_price, area, plot_price, area_price = get_city_default_values(location)
       sp.update_city(location, elec_price, area)
    else:
       sp.update_parameter(area, hc, eff, elec_price)
    df = sp.df_hourly
    fig = px.bar(df, x="datetime", y="solar_pwr", range_y=[0,125], title="Power production [kWh] last 48 hours" )
    fig['layout']['xaxis1'].update(title_text='Date')
    fig['layout']['yaxis1'].update(title_text='Power [kWh]')
    fig2 = create_weather_chart(df)
    temp  = sp.df_current.iloc[0]['temp']
    uvi   = sp.df_current.iloc[0]['uvi']
    power = sp.df_current.iloc[0]['solar_pwr']
    power24 = sp.get_last_24()['solar_pwr']
    profit24 = power24*elec_price/100
    currentDiv = create_current_div(temp,uvi,power,power24,profit24, location)

    return fig, fig2, currentDiv

liveDiv = html.Div([
             html.H4('Live Feed',style={"padding":"1em" }),
             html.Div(id='live-update-text'),
             currentPower,
             currentWeather,
             dcc.Interval(
              id='interval-component',
              interval=1*5000, # in milliseconds
              n_intervals=0
            )
          ])


# investmentboard html
liveBoardDiv= html.Div(
    [
        dbc.Row(
            [
             dbc.Col([html.H4('Parameters', style={"padding":"1em"}),
               cityDiv,areaDiv, spEffDiv, spHcDiv,elecPriceDiv,typeDiv,
               html.Div([areaPriceDiv,spPriceDiv,performanceDiv], style={'display':'none'})
            ],
            width=4, style={'margin-left': '4em'}),
            dbc.Col(liveDiv , width=6)
            ]
        ),
    ]
)
