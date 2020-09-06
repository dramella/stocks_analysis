import dash
import dash_table
from dash.dependencies import Input, Output, State
from dash_extensions import Download
import dash_core_components as dcc
import dash_html_components as html
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,suppress_callback_exceptions=True,external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True




app.layout = html.Div([
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1'),
        dcc.Tab(label='Tab two', value='tab-2'),
    ]),
    html.Div(id='tabs-example-content')
])

@app.callback(Output('tabs-example-content', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content 1')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])


