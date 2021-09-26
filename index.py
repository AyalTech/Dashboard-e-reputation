import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State

from app import app
from panels import statistiques, recommandations, analyse_sentiment

opportunities = pd.read_csv('data/extracted_tweets.csv',  sep=";")
cases = pd.read_csv('data/extracted_tweets.csv', sep=";")
leads = pd.read_csv('data/extracted_tweets.csv', sep=';')
server = app.server
app.title = 'Dashboard e-réputation'
app.layout = html.Div(
    [
        html.Div(
            className="row header",
            children=[
                html.Button(id="menu", children=dcc.Markdown("&#8801")),
                html.Span(
                    className="app-title",
                    children=[
                        dcc.Markdown("**Dashboard**"),
                        html.Span(
                            id="subtitle",
                            children=dcc.Markdown("&nbsp e-réputation"),
                            style={"font-size": "1.8rem", "margin-top": "15px"},
                        ),
                    ],
                )
            ],
        ),
        html.Div(
            id="tabs",
            className="row tabs",
            children=[
                dcc.Link("Statistiques", href="/"),
                dcc.Link("Analyse de sentiment", href="/"),
                dcc.Link("Recommandations", href="/"),
            ],
        ),
        html.Div(
            id="mobile_tabs",
            className="row tabs",
            style={"display": "none"},
            children=[
                dcc.Link("Statistiques", href="/"),
                dcc.Link("Analyse de sentiment", href="/"),
                dcc.Link("Recommandations", href="/"),
            ],
        ),
        dcc.Store(  # opportunities df
            id="opportunities_df",
            data=opportunities.to_json(orient="split"),
        ),
        dcc.Store(  # leads df
            id="leads_df",
            data=leads.to_json(orient="split"),
        ),
        dcc.Store(
            id="cases_df",
            data=cases.to_json(orient="split"),
        ),  # cases df
        dcc.Location(id="url", refresh=False),
        html.Div(id="tab_content"),
        html.Link(
            href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",
            rel="stylesheet",
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"
        ),
    ],
    className="row",
    style={"margin": "0%"},
)

# Update the index


@app.callback(
    [
        Output("tab_content", "children"),
        Output("tabs", "children"),
        Output("mobile_tabs", "children"),
    ],
    [Input("url", "pathname")],
)
def display_page(pathname):
    tabs = [
        dcc.Link("Statistiques", href="/dash-ppd/statistiques"),
        dcc.Link("Analyse de sentiment", href="/dash-ppd/analyse_sentiment"),
        dcc.Link("Recommandations", href="/dash-ppd/recommandations"),
    ]
    if pathname == "/dash-ppd/statistiques":
        tabs[0] = dcc.Link(
            dcc.Markdown("**&#9632 Statistiques**"),
            href="/dash-ppd/statistiques",
        )
        return statistiques.layout, tabs, tabs
    elif pathname == "/dash-ppd/recommandations":
        tabs[2] = dcc.Link(
            dcc.Markdown("**&#9632 Recommandations**"), href="/dash-ppd/recommandations"
        )
        return recommandations.layout, tabs, tabs
    tabs[1] = dcc.Link(
        dcc.Markdown("**&#9632 Analyse de sentiment**"), href="/dash-ppd/analyse_sentiment"
    )
    return analyse_sentiment.layout, tabs, tabs


@app.callback(
    Output("mobile_tabs", "style"),
    [Input("menu", "n_clicks")],
    [State("mobile_tabs", "style")],
)
def show_menu(n_clicks, tabs_style):
    if n_clicks:
        if tabs_style["display"] == "none":
            tabs_style["display"] = "flex"
        else:
            tabs_style["display"] = "none"
    return tabs_style


if __name__ == "__main__":
    app.run_server(debug=False)
