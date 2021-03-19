import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from widgets import *
from staticDataBoard import *
from InvestSPModel import InvestSPModel
from app import app 

location = df_cities.index.values[0]
sp_type  = df_solar.index.values[0]
elec_price, area, plot_price, area_price = get_city_default_values(location)
eff, hc, sp_price = get_sp_default_values(sp_type)
im = InvestSPModel(df_cities.index.values)
im.set_location(location, 75, eff, area, elec_price, area_price, sp_price)

revenueChart =  dcc.Graph(id="revenue-bar-chart")
profitChart =  dcc.Graph(id="profit-bar-chart")
powerChart =  dcc.Graph(id="power-bar-chart")
def create_nasa_chart(im):
    fig = px.bar(im.df_nasa, x="month", y="irradiance_m2", color='location', title="30-year averaged irradiance data", labels={'month':'Month','irradiance_m2': "Irradiance [kWh/m2/day]", 'location':'Location'}, barmode="group" )
    return fig
nasa_chart = dcc.Graph(figure=create_nasa_chart(im))



@app.callback(
    [Output("revenue-bar-chart", "figure"), 
     Output("profit-bar-chart", "figure"), 
     Output("power-bar-chart", "figure")], 
    [Input("cityDropdown", "value"),
     Input("typeRadio", "value"),
     Input('areaPriceSlider', 'value'),
     Input("elecPriceSlider", "value"),
     Input("areaSlider", "value"),
     Input("spEffSlider", "value"),
     Input('spPriceSlider', 'value'),
     Input("spHcSlider", "value"),
     Input("performanceSlider", "value")
      ])
def generate_chart(location, sp_type, land_price,elec_price, area, eff, sp_price, hc, performance):
    ctx = dash.callback_context
    wid = ctx.triggered[0]['prop_id'].split('.')[0]
    if (wid=="cityDropdown"):
       elec_price, area, plot_price, area_price = get_city_default_values(location)
       im.set_location(location, performance, eff, area, elec_price, land_price, sp_price)
    elif (wid=='typeRadio'):
       eff, hc, sp_price = get_sp_default_values(sp_type)
       im.calc_performance(performance, eff, area, elec_price, land_price, sp_price)
    else:
       im.calc_performance(performance, eff, area, elec_price, land_price, sp_price)
    df = im.df
    fig_rev = px.bar(df, x="date", y="revenue", range_y=[0, 10e3], title="Expected revenue per month [euro]",
		         labels={'date':'Date','revenue': "Revenue [euro]"}
                    )
    fig_rev.update_traces(marker_color='blue')
    fig_prof = px.bar(df, x="date", y="profit", title="Expected profit over time [euro]", color='loss',color_discrete_sequence =['red','green'], labels={'date':'Date','profit': "Net Profit [euro]", 'loss':'Net result'} )
    fig_pow = px.bar(df, x="date", y="power", range_y=[0, 100e3], title="Expected Power produced per month [kWh]",
                     labels={'date':'Date','power': "Power [kWh]"})
    fig_pow.update_traces(marker_color='orange')
    return fig_rev, fig_prof, fig_pow

# investmentboard html
investmentBoardDiv= html.Div(
    [
        dbc.Row(
            [
             dbc.Col([html.H4('Parameters', style={"padding":"1em"}),
               cityDiv,areaDiv, spEffDiv,elecPriceDiv,typeDiv, html.Div(spHcDiv,style={'display':'none'}),
               html.Div([areaPriceDiv,spPriceDiv,performanceDiv], style={'display':'block'})
            ],
            width=4, style={'margin-left': '4em'}), 
              dbc.Col([html.Div(powerChart),html.Div(revenueChart),html.Div(profitChart), html.Div(nasa_chart, style={'width':'50%'})] , width=6)
            ]
        ),
    ]
)
