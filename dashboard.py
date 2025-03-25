# Ensure required packages are installed with:
# pip install dash dash-bootstrap-components requests

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import requests

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("OpenShift Deployment Dashboard"), className="mt-4 mb-4")
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='env-selector',
                options=[
                    {'label': 'Development', 'value': 'dev'},
                    {'label': 'SIT', 'value': 'sit'},
                    {'label': 'UAT', 'value': 'uat'},
                    {'label': 'Pre-Production', 'value': 'preprod'}
                ],
                value='dev',
                clearable=False
            )
        ], width=4),

        dbc.Col([
            dcc.Dropdown(id='deployment-selector', placeholder="Select Deployment")
        ], width=4),

        dbc.Col([
            dbc.Button("Get Logs", id='fetch-logs-btn', color='primary')
        ], width=2)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H5("Deployments"),
            html.Div(id="deployments-table")
        ])
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Pod Logs"),
            html.Pre(id="pod-logs", style={"height": "400px", "overflow": "auto", "background": "#f8f9fa", "padding": "10px"})
        ])
    ], className="mt-4")
], fluid=True)

@app.callback(
    Output('deployments-table', 'children'),
    Output('deployment-selector', 'options'),
    Input('env-selector', 'value')
)
def update_deployments(env):
    api_url = f"http://localhost:5000/{env}"
    try:
        deployments = requests.get(api_url).json()
    except requests.RequestException as e:
        deployments = []
        print(f"Error fetching deployments: {e}")

    table_header = [html.Thead(html.Tr([html.Th("Name"), html.Th("Image"), html.Th("Status")]))]
    rows = [html.Tr([html.Td(dep['name']), html.Td(dep['image']), html.Td(dep['ready'])]) for dep in deployments]
    table_body = [html.Tbody(rows)]

    deployment_options = [{'label': dep['name'], 'value': dep['name']} for dep in deployments]

    return dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True), deployment_options

@app.callback(
    Output('pod-logs', 'children'),
    Input('fetch-logs-btn', 'n_clicks'),
    State('env-selector', 'value'),
    State('deployment-selector', 'value')
)
def fetch_logs(n_clicks, env, deployment_name):
    if n_clicks and deployment_name:
        api_url = f"http://localhost:5000/{env}-logs/{deployment_name}"
        try:
            logs_data = requests.get(api_url).json()
            return logs_data.get("logs", "No logs found or unable to fetch logs.")
        except requests.RequestException as e:
            print(f"Error fetching logs: {e}")
            return "Error fetching logs."
    return "Logs will appear here after selecting deployment and clicking the button."

if __name__ == '__main__':
    app.run_server(debug=True)
