import dash
from dash import Dash, html, dcc, dash_table, Input, Output, State
import requests
import pandas as pd

API_URL = "http://localhost:5000"

app = Dash(__name__)

app.layout = html.Div(style={'padding': '20px', 'fontFamily': 'Arial'}, children=[
    html.H2('OpenShift Deployments Dashboard', style={'color': '#007bff'}),

    html.Div([
        html.Label('Select Environment:', style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='env-dropdown',
            options=[
                {'label': 'DEV', 'value': 'dev'},
                {'label': 'SIT', 'value': 'sit'},
                {'label': 'UAT', 'value': 'uat'},
                {'label': 'PREPROD', 'value': 'preprod'}
            ],
            value='dev',
            clearable=False,
            style={'width': '200px'}
        ),
    ], style={'marginBottom': '20px'}),

    html.Button('Load Deployments', id='load-btn', n_clicks=0, style={
        'backgroundColor': '#007bff', 'color': 'white', 'border': 'none', 'padding': '10px', 'cursor': 'pointer'
    }),

    html.Div(id='deployments-table', style={'marginTop': '30px'}),

    html.H3('Pod Logs:', style={'marginTop': '40px'}),
    html.Div(id='logs-container', style={
        'whiteSpace': 'pre-wrap', 
        'backgroundColor': '#f8f9fa', 
        'padding': '10px',
        'borderRadius': '5px',
        'height': '400px',
        'overflowY': 'scroll'
    })
])

@app.callback(
    Output('deployments-table', 'children'),
    Input('load-btn', 'n_clicks'),
    State('env-dropdown', 'value')
)
def update_deployments(n_clicks, env):
    if n_clicks == 0:
        return ""

    response = requests.get(f"{API_URL}/{env}")
    if response.status_code != 200:
        return html.Div('Failed to fetch deployments', style={'color': 'red'})

    deployments = response.json()
    df = pd.DataFrame(deployments)

    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        row_selectable='single',
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': '#007bff', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'padding': '10px', 'textAlign': 'left'},
    )

@app.callback(
    Output('logs-container', 'children'),
    Input('table', 'selected_rows'),
    State('table', 'data'),
    State('env-dropdown', 'value')
)
def display_logs(selected_rows, rows, env):
    if selected_rows is None or len(selected_rows) == 0:
        return 'Select a deployment to view logs.'

    deployment_name = rows[selected_rows[0]]['name']
    response = requests.get(f"{API_URL}/{env}-logs/{deployment_name}")

    if response.status_code != 200:
        return 'Failed to fetch logs.'

    logs = response.json().get('logs', 'No logs available.')

    return logs

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
