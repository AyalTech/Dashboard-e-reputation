import base64
from datetime import date
import plotly
from dash.dependencies import Input, Output, State
from app import app, indicator, millify, df_to_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff
from piplines import analysis
import random
import igraph as ig
from wordcloud import WordCloud


mentions_df = pd.read_csv('data/top_mentions.csv', sep=';')


def top_users():
    table_data = pd.read_csv('data/users.csv', sep=";").head(10)
    fig = ff.create_table(table_data, height_constant=25)
    figure1 = go.Figure(data=fig, layout=go.Layout())
    return figure1


def sentiment_pi_chart():
    labels = ['Négatif', 'Positf', 'Neutre']
    values = [analysis.SentimentAnalysis.NEGATIVE_PERCENTAGE,
              analysis.SentimentAnalysis.POSITIVE_PERCENTAGE,
              analysis.SentimentAnalysis.NEUTRAL_PERCENTAGE]

    # Use `hole` to create a donut-like pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.7)])
    return fig


def converted_opportunities(period, source, df):
    df = pd.read_csv("data/extracted_tweets.csv", sep=';')
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
            3 * 30, unit="d")]
    elif period == "12":
        df_final = df_final.loc[df_final["Created On"] >= pd.to_datetime(df_final["Created On"]) - pd.to_timedelta(
            12 * 30, unit="d")]
    # if no results were found
    if df.empty:
        layout = dict(
            autosize=True, annotations=[dict(text="No results found", showarrow=False)]
        )
        return {"data": [], "layout": layout}

    trace = go.Scatter(
        x=df_final["Created On"],
        y=df_final["isRetweeted"] + 1,
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
                       textfont={'size': weights,
                                 'color': colors})
    layout1 = go.Layout({
        'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
        "height": 400})
    graph_props = {'data': data1, 'layout': layout1}
    fig = go.Figure(graph_props)
    return fig


def word_cloud_2():
    words_df = pd.read_csv('data/clean_tweets.csv', sep=";")
    # word cloud visualization
    allWords = ' '.join([twts for twts in words_df['text_clean'].astype(str)])
    wordCloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110, background_color="white").generate(
        allWords)
    wordCloud.to_file('data/wordcloud.png')


#
word_cloud_2()
coclust_img = 'data/coclust.jpg'
graph_img = 'data/graph.png'
wordcloud_img = 'data/wordcloud.png'
coclust_img_base64 = base64.b64encode(open(coclust_img, 'rb').read()).decode('ascii')
graph_img_base64 = base64.b64encode(open(graph_img, 'rb').read()).decode('ascii')
wordcloud_img_base64 = base64.b64encode(open(wordcloud_img, 'rb').read()).decode('ascii')


def graph_layout():
    G = ig.Graph.Read_Lgl('data/graph.txt')
    labels = list(G.vs['name'])
    N = len(labels)
    E = [e.tuple for e in G.es]  # list of edges
    layt = G.layout('kk')  # kamada-kawai layout
    Xn = [layt[k][0] for k in range(N)]
    Yn = [layt[k][1] for k in range(N)]
    Xe = []
    Ye = []
    for e in E:
        Xe += [layt[e[0]][0], layt[e[1]][0], None]
        Ye += [layt[e[0]][1], layt[e[1]][1], None]

    trace1 = go.Scatter(x=Xe,
                        y=Ye,
                        mode='lines',
                        line=dict(color='rgb(210,210,210)', width=1),
                        hoverinfo='none'
                        )
    trace2 = go.Scatter(x=Xn,
                        y=Yn,
                        mode='markers',
                        name='ntw',
                        marker=dict(symbol='circle-dot',
                                    size=5,
                                    color='#6959CD',
                                    line=dict(color='rgb(50,50,50)', width=0.5)
                                    ),
                        text=labels,
                        hoverinfo='text'
                        )

    axis = dict(showline=False,  # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
                )

    width = 800
    height = 800
    layout = go.Layout(
        font=dict(size=12),
        showlegend=False,
        autosize=False,
        width=width,
        height=height,
        xaxis=axis,
        yaxis=axis,
        margin=dict(
            l=40,
            r=40,
            b=85,
            t=100,
        ),
        hovermode='closest',
        annotations=[
            dict(
                showarrow=False,
                text='',
                xref='paper',
                yref='paper',
                x=0,
                y=-0.1,
                xanchor='left',
                yanchor='bottom',
                font=dict(
                    size=14
                )
            )
        ]
    )

    data = [trace1, trace2]
    return go.Figure(data=data, layout=layout)


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
                id="new_opportunity_2",
                n_clicks=0,
                className="button pretty_container",
            ),
            html.Div(
                id="opportunity_indicators",
                className="row indicators",
                children=[
                    indicator(
                        "#00cc96", "Sentiment positif", "sentiment_positifs_indicator"
                    ),
                    indicator(
                        "#119DFF",
                        "Tweets analysés",
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
                    html.P("Repartition des sentiments"),
                    dcc.Graph(
                        id="pie_chart",
                        config=dict(displayModeBar=False),
                        figure=sentiment_pi_chart(),
                    ),
                ],
            ),
            html.Div(
                id="opportunity_heatmap",
                className="chart_div pretty_container",
                children=[
                    html.P('Nuage de mots'),
                    html.Img(src='data:image/png;base64,{}'.format(wordcloud_img_base64), className="center")
                    # dcc.Graph(id='wordcloud', config=dict(displayModeBar=False), figure=word_cloud())
                ],
            ),
            html.Div(
                id="top_open_container",
                className="pretty_container",
                children=[
                    html.Div([html.P("Co-clustring")], className="subtitle"),
                    html.Img(src='data:image/png;base64,{}'.format(coclust_img_base64))
                ],
            ),
            html.Div(
                id="top_lost_container",
                className="pretty_container",
                children=[
                    html.Div([html.P("Graph")], className="subtitle"),
                    # dcc.Graph(id='graph', config=dict(displayModeBar=False), figure=graph_layout())

                    html.Img(src='data:image/png;base64,{}'.format(graph_img_base64))
                ],
            ),

        ], className="pretty_container")]


@app.callback(
    Output("sentiment_positifs_indicator", "children"),
    [Input("opportunities_df", "data")],
)
def sentiment_positifs_indicator_callback(df):
    return dcc.Markdown("**{}**".format(analysis.SentimentAnalysis.POSITIVE_PERCENTAGE) + "%")
