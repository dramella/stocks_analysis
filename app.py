import dash
import dash_table
from dash.dependencies import Input, Output, State
from dash_extensions import Download
import dash_core_components as dcc
import dash_html_components as html
from dash_extensions.snippets import send_data_frame
from lib import df_line_graph,yf_historical_data,summary_info

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,suppress_callback_exceptions=True,external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.H1('Stock Analysis Dashboard'),
    dcc.Markdown(''' --- '''),
    dcc.Input(id='my-id', value='ticker', type="text"),
    html.Button('Enter', id='button'),
    html.Div(id='my-div'),
    dcc.Graph(id='output-graph',style={'display': 'none'}),
    html.Div([html.Button("Download Excel Data", id="btn",style={'display': 'none'}), Download(id="download")]),
    html.Div([html.Div(id="table1")])])

@app.callback(
    Output('output-graph', "figure"),
    Output('output-graph', 'style'),
    [Input("button", "n_clicks")],
    [State("my-id", "value")],
)
def update_figure(n_clicks, value):
    if n_clicks is not None:
        return df_line_graph(df=yf_historical_data(ticker=value,end_date=None, start_date=None,freq='Daily'),y='Close'),{'display':'block'}


@app.callback(
    Output("btn", "style"),
    [Input("button", "n_clicks")])

def show_button(n_clicks):
    if n_clicks>=1:
        return {'display': 'block'}

@app.callback(
    Output("download", "data"),
    [Input("btn", "n_clicks")],
    [State("my-id", "value")]
)

def generate_csv(n_clicks,value):
    if n_clicks is not None:
        df=yf_historical_data(ticker=value,end_date=None, start_date=None,freq='Daily')
        return send_data_frame(df.to_excel, filename=f"{value}.xlsx")

@app.callback(
    Output('table1', 'children'),
    [Input("button", "n_clicks")],
    [State("my-id", "value")]
)

def update_table(n_clicks,value):
    if n_clicks is None:
        return dash.no_update
    else:
        df=summary_info(value)
        data = df.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (df.loc[0].to_dict())]
        return dash_table.DataTable(data=data, columns=columns)

if __name__ == '__main__':
    app.run_server()


