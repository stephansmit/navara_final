import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from investmentBoard import investmentBoardDiv
from staticDataBoard import staticDataBoardDiv
from liveBoard import liveBoardDiv
from app import app

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-0', children=[
        dcc.Tab(label='Live board', value='tab-0'),
        dcc.Tab(label='Investment board', value='tab-1'),
        dcc.Tab(label='Static data', value='tab-2'),
    ]),
    html.Div(id='tabs-content',children = liveBoardDiv)
])

@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-0':
        return liveBoardDiv
    if tab == 'tab-1':
        return investmentBoardDiv
    elif tab == 'tab-2':
        return staticDataBoardDiv

if __name__ == '__main__':
    app.run_server(debug=True)

