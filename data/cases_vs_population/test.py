
#!/usr/bin/env python


import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import fire
import pandas as pd
import plotly.express as px
import webbrowser
from threading import Timer
from dash.dependencies import Input, Output, State

import datetime

from gs_quant.data import Dataset
from gs_quant.session import GsSession, Environment

def render_app(df: pd.DataFrame):


    graph = dcc.Graph(
        figure=px.line(
            df, x="updateTime", y="casePopulation", color='countryId', template="seaborn"
        ),
    )

    case_vs_country = html.Div(
        [
            html.H3(
                "New Cases as a Percentage of Population",
                style={
                    "textAlign": "center",
                    "fontWeight": "bold"
                }
            ),
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='New Cases as a Percentage of Population'
            ),
            dbc.Row([dbc.Col(graph)], className="row mb-2"),
        ]
    )

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
    app.layout = dbc.Container([case_vs_country],
                                style={"padding-top": "50px"},)

    return app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:2000/")

def main() -> None:
#    df = pd.read_json(filename)
    GsSession.use(Environment.PROD, '77d7c80dec0b44e9868dfaa3a7e2cb36', '4edbc70b2249de3ddc9f303bb373575cb06839fb6857570648fdb772ccf8e377', ('read_product_data',))
    ds = Dataset('COVID19_COUNTRY_DAILY_ECDC')
    df = ds.get_data(start = datetime.date(2019,12,31), end=datetime.date(2020,6,18), countryId=["US", "GB", "BR", "NZ", "IN"])
    df["casePopulation"] = df["newConfirmed"]/df["population"]
    print(df)
    app = render_app(df)
    app.run_server(port=2000)


if __name__ == "__main__":
    Timer(1, open_browser).start()
    fire.Fire(main)
