
#!/usr/bin/env python


import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import fire
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import webbrowser
from threading import Timer
from dash.dependencies import Input, Output, State

import datetime

from gs_quant.data import Dataset
from gs_quant.session import GsSession, Environment

def render_app(df_ecdc: pd.DataFrame, data_who: pd.DataFrame):

    countries = set(data_who['countryName'])
    line_p = go.Figure()
    x = data_who.index

    for each in countries:
        y = data_who.loc[data_who['countryName'] == each]
        line_p.add_trace(go.Scatter(x=x, y=((y['totalFatalities']/y['totalConfirmed'])*100), mode='lines', name=each, line=dict( dash='dot'), connectgaps=True,))
        y = data_who.groupby([data_who.index]).sum()
        line_p.add_trace(go.Scatter(x=x, y=((y['totalFatalities']/y['totalConfirmed'])*100), mode='lines', name="Average"))
        line_p.update_xaxes(rangeslider_visible=True, rangeselector=dict(buttons=list([
        dict(count=1, label="1m", step="month", stepmode="backward"),
        dict(count=6, label="6m", step="month", stepmode="backward"),
        dict(count=1, label="YTD", step="year", stepmode="todate"),
        dict(count=1, label="1y", step="year", stepmode="backward"),
        dict(step="all")
        ])),title="Date")

        line_p.update_yaxes(title="Percentage of Fatalities/Confirmed Cases")

        line_p.update_layout(title="Total Fatalities as a Percentage of Total COVID-19 Cases")

        #Total cases by country
        who_group = data_who.groupby([data_who.index]).cumsum()

        bar = go.Figure()
        bar.add_trace(go.Histogram(histfunc="sum", x=data_who['countryName'], y= data_who['newConfirmed'], name="Total Confirmed Cases"))
        bar.add_trace(go.Histogram(histfunc="sum", x=data_who['countryName'], y= data_who['newFatalities'], name="Total Fatalities"))

        bar.update_layout(barmode='overlay')

        bar.update_traces(opacity=0.5)

        bar.update_layout(title="Total Fatalities vs Total COVID-19 Cases by country")

        bar.update_xaxes(title="Country")

        bar.update_yaxes(title="Cumulative Amount")

    graph_case_population = dcc.Graph(
        figure=px.line(
            df_ecdc, x="updateTime", y="casePopulation", color='countryId', template="seaborn"
        ),
    )

    graph_rate_of_change = dcc.Graph(
        figure=px.line(
            df_ecdc, x="updateTime", y="rateOfChange", color='countryId', template="seaborn"
        ),
    )

    graph_death_total_line = dcc.Graph(
        figure = line_p
    )

    graph_death_total_bar = dcc.Graph(
        figure = bar
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
            # dcc.Dropdown(
            #     id='xaxis-column',
            #     options=[{'label': i, 'value': i} for i in available_indicators],
            #     value='New Cases as a Percentage of Population'
            # ),
            dbc.Row([dbc.Col(graph_case_population)], className="row mb-2"),
        ]
    )

    header = dbc.Jumbotron(
        [
            html.H1("C-M Dashboard", className="display-6"),
            html.P(
                "To extract meaningful data from various data sources, by leveraging the Marquee API, "
                " and present them to users in a clear and informative manner. ",
                className="lead",
            ),
            html.Hr(className="my-4"),
            html.P(
                [
                    "Data sources: ",
                    html.A(
                        "World Health Organization (WHO)",
                        href='https://covid19.who.int/',
                        target="_blank"
                    ),
                    ", ",
                    html.A(
                        "European Centre for Disease Prevention and Control (ECDC)",
                        href='https://data.europa.eu/euodp/en/data/dataset/covid-19-coronavirus-data',
                        target="_blank"
                    ),
                    ", and ",
                    html.A(
                        "Wikipedia",
                        href='https://en.wikipedia.org/wiki/Template:2019%E2%80%9320_coronavirus_pandemic_data',
                        target="_blank"
                    ),
                    "."
                ]
            )
        ],
    )

    rate_of_change = html.Div(
        [
            html.H3(
                "Rate of Change Over Time",
                style={
                    "textAlign": "center",
                    "fontWeight": "bold"
                }
            ),
            dbc.Row([dbc.Col(graph_rate_of_change)], className="row mb-2"),
        ]
    )

    death_total = html.Div(
        [
            html.H3(
                "Total Deaths as a Proportion of Total Cases",
                style={
                    "textAlign": "center",
                    "fontWeight": "bold"
                }
            ),
            dbc.Row(
                [
                    dbc.Col(graph_death_total_line),
                    dbc.Col(graph_death_total_bar)
                ],
                style={"padding": "10px"},
                className="row align-items-center mb-2",
            ),
        ]
    )

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
    app.layout = dbc.Container([header, case_vs_country, death_total, rate_of_change],
                                style={"padding-top": "50px"},)

    return app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:2000/")

def main() -> None:
#    df = pd.read_json(filename)
    GsSession.use(Environment.PROD, '77d7c80dec0b44e9868dfaa3a7e2cb36', '4edbc70b2249de3ddc9f303bb373575cb06839fb6857570648fdb772ccf8e377', ('read_product_data',))
    ds_ecdc = Dataset('COVID19_COUNTRY_DAILY_ECDC')
    ds_who = Dataset('COVID19_COUNTRY_DAILY_WHO')

    data_who = ds_who.get_data(datetime.date(2020, 1, 21), countryId=["US", "GB", "IN", "BR", "NG", "NZ"])

    df_ecdc = ds_ecdc.get_data(start = datetime.date(2019,12,31), end=datetime.date(2020,6,18), countryId=["US", "GB", "BR", "NZ", "IN", "NG"])
    df_ecdc["casePopulation"] = df_ecdc["newConfirmed"]/df_ecdc["population"]
    df_ecdc['rateOfChange'] = (df_ecdc['newConfirmed'] - df_ecdc['newConfirmed'].shift())/df_ecdc['newConfirmed'].shift()
    df_ecdc['rateOfChange'] = df_ecdc['rateOfChange'].fillna(0)

    print(data_who)

    app = render_app(df_ecdc, data_who)
    app.run_server(port=2000)


if __name__ == "__main__":
    Timer(1, open_browser).start()
    fire.Fire(main)
