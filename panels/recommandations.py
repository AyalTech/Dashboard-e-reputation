from datetime import date
import plotly
from dash.dependencies import Input, Output, State
from app import app, indicator, millify, df_to_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff
import random
import pycountry
import numpy as np

mentions_df = pd.read_csv('data/top_mentions.csv', sep=';')


def top_users():
    table_data = pd.read_csv('data/users.csv', sep=";").head(10)
    fig = ff.create_table(table_data, height_constant=25)
    figure1 = go.Figure(data=fig, layout=go.Layout())
    return figure1

def top_used_words():
    words_df = pd.read_csv('data/words.csv', sep=";").head(10)
    figure = go.Figure(data= go.Bar(x=words_df['count'], y=words_df['words'], orientation='h'), layout=go.Layout(
        height=400
        ))
    return figure

def get_country(text):
    country_res = np.nan
    for country in pycountry.countries:
        if country.name.lower() in text.lower():
            country_res = country.alpha_3
    return country_res


def get_country_df():
    df = pd.read_csv('data/extracted_tweets.csv', sep=';')
    df['user_location'] = df['user_location'].astype(str)
    df.dropna(subset=['user_location'], inplace=True)
    df['Country'] = df['user_location'].apply(get_country)
    df.dropna(subset=['Country'], inplace=True)
    df_country = df.groupby(['Country']).sum().reset_index()
    df_country.replace(0, 1, inplace=True)
    code_df = pd.read_csv('data/2014_world_gdp_with_codes.csv')
    df_country_code = df_country.merge(code_df, left_on='Country', right_on='CODE', how='left')

    return df_country_code


def worldmap():
    dff = get_country_df()
    dff['hover_text'] = dff["COUNTRY"]
    dff['sum'] = np.random.normal(100, 92, dff['hover_text'].shape[0])
    trace = go.Choropleth(locations=dff['CODE'], z=np.log(dff['sum']),
                          text=dff['hover_text'],
                          hoverinfo="text",
                          marker_line_color='white',
                          autocolorscale=False,
                          reversescale=True,
                          colorscale="RdBu", marker={'line': {'color': 'rgb(180,180,180)', 'width': 0.5}},
                          colorbar={"thickness": 10, "len": 0.3, "x": 0.9, "y": 0.7,
                                    'title': {"text": 'persons', "side": "bottom"},
                                    'tickvals': [2, 10],
                                    'ticktext': ['100', '100,000']})
    return go.Figure(data=[trace],
                     layout=go.Layout(height=800, geo={'showframe': False, 'showcoastlines': False,
                                                       'projection': {'type': "miller"}}))

def converted_opportunities(period, source, df):
    df = pd.read_csv("data/extracted_tweets.csv", sep =';')
    df["Created On"] = pd.to_datetime(df["created_at"])

    # source filtering
    if source == "all_s":
        df_final = df
    else:
        df_final = df.loc[df["source"] == source]

    # period filtering
    if period == "1":
        df_final = df_final.loc[df_final["Created On"] >= pd.to_datetime(df_final["Created On"]) - pd.to_timedelta(
            30, unit="d")]
    elif period == "3":
        df_final = df_final.loc[df_final["Created On"] >= pd.to_datetime(df_final["Created On"]) - pd.to_timedelta(
            3*30, unit="d")]
    elif period == "12":
        df_final = df_final.loc[df_final["Created On"] >= pd.to_datetime(df_final["Created On"]) - pd.to_timedelta(
            12*30, unit="d")]
    # if no results were found
    if df.empty:
        layout = dict(
            autosize=True, annotations=[dict(text="No results found", showarrow=False)]
        )
        return {"data": [], "layout": layout}

    trace = go.Scatter(
        x=df_final["Created On"],
        y=df_final["isRetweeted"] +1,
        name="converted opportunities",
        fill="tozeroy",
        fillcolor="#e6f2ff",
    )

    data = [trace]

    layout = go.Layout(
        autosize=True,
        xaxis=dict(showgrid=False),
        margin=dict(l=35, r=25, b=23, t=5, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


# returns heat map figure
def heat_map_fig(df, x, y):
    z = []
    for lead_type in y:
        z_row = []
        for stage in x:
            probability = df[(df['screen_name'] == stage) & (df["Type"] == lead_type)][
                "Probability"
            ].mean()
            z_row.append(probability)
        z.append(z_row)

    trace = dict(
        type="heatmap", z=z, x=x, y=y, name="mean probability", colorscale="Blues"
    )
    layout = dict(
        autosize=True,
        margin=dict(t=25, l=210, b=85, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return go.Figure(data=[trace], layout=layout)


# returns top 5 open opportunities
def top_open_opportunities(df):
    df = df.sort_values("user_followers_count", ascending=False)
    cols = ['screen_name', "user_location", "user_followers_count", "source"]
    df = df[cols].iloc[:5]
    # only display 21 characters
    df["screen_name"] = df["screen_name"].apply(lambda x: x[:30])
    return df_to_table(df)


def word_cloud():
    words_df = pd.read_csv('data/words.csv', sep=";")
    words = words_df['words'].to_list()
    colors = [plotly.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(30)]
    weights = words_df['count'].to_list()

    data1 = go.Scatter(x=[random.random() for i in range(30)],
                       y=[random.random() for i in range(30)],
                       mode='text',
                       text=words,
                       marker={'opacity': 0.3},
                       textfont={'size': weights * 20,
                                 'color': colors})
    layout1 = go.Layout({
        'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
        "height": 300})
    graph_props = {'data': data1, 'layout': layout1}
    return graph_props

# returns modal (hidden by default)

layout = [
    html.Div(
        id="opportunity_grid",
        children=[
            html.Div(
                className="control dropdown-styles",
                children=dcc.Dropdown(
                    id="converted_opportunities_dropdown",
                    options=[
                        {"label": "1 Mois", "value": "1"},
                        {"label": "3 Mois", "value": "3"},
                        {"label": "12 Mois", "value": "12"},
                    ],
                    value="D",
                    clearable=False,
                ),
            ),

            html.Div(
                className="control dropdown-styles",
                children=dcc.Dropdown(
                    id="source_dropdown",
                    options=[
                        {"label": "Sources", "value": "all_s"},
                        {"label": "Web App", "value": "Web App"},
                        {"label": "iPhone", "value": "iPhone"},
                        {"label": "Android", "value": "Android"},
                    ],
                    value="all_s",
                    clearable=False,
                ),
            ),
            html.Span(
                "Amazon",
                id="new_opportunity_",
                n_clicks=0,
                className="button pretty_container",
            ),
            html.Span(
                "Apple",
                id="new_opportunity_2",
                n_clicks=0,
                className="button pretty_container",
            ),
            html.Div(
                id="opportunity_indicators",
                className="row indicators",
                children=[
                    indicator(
                        "#00cc96", "Mentions", "left_opportunities_indicator"
                    ),
                    indicator(
                        "#119DFF",
                        "Tweets",
                        "middle_opportunities_indicator",
                    ),
                    indicator(
                        "#EF553B", "Utilisateurs uniques", "right_opportunities_indicator"
                    ),
                ],
            ),
            html.Div(
                id="converted_count_container",
                className="chart_div pretty_container",
                children=[
                    html.P("Volume de tweet"),
                    dcc.Graph(
                        id="converted_count",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
            ),
            html.Div(
                id="opportunity_heatmap",
                className="chart_div pretty_container",
                children=[
                    html.P('Termes les plus fréquents'),
                    dcc.Graph(id='top_used_words',
                              config=dict(displayModeBar=False),
                              figure=top_used_words())
                ],
            ),
            html.Div(
                id="top_open_container",
                className="pretty_container",
                children=[
                    html.Div([html.P("Top Utilisateurs")], className="subtitle"),
                    dcc.Graph(id='top_users',
                              config=dict(displayModeBar=False),
                              figure=top_users())
                    # html.Div(id="top_open_opportunities", className="table"),
                ],
            ),
            html.Div(
                id="top_lost_container",
                className="pretty_container",
                children=[
                    html.Div([html.P("Répartition par pays")], className="subtitle"),
                    dcc.Graph(id="worldmap",
                              config=dict(displayModeBar=False),
                              figure=worldmap()
                              )
                ],
            ),

        ], className="pretty_container")]





