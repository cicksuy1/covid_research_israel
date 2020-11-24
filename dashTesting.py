import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask, Response, request,render_template,url_for
from Ploty_Dash_learn.generate_plots import globalvars_class as plotmaker
import plotly.graph_objects as go
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

test= plotmaker()
cov_pos = test.daily_covid_positive

fig = go.Figure()
fig.add_trace(go.Bar(
    x=cov_pos.index,
    y=cov_pos["corona_result"],name="bars"))
fig.add_trace(go.Scatter(
    x=cov_pos.index,
    y=cov_pos["corona_result"],name="CovidPositive",mode="lines"))



app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    dcc.Input(
        id='graph_ma',
        type='number',
        value=7
    ),
    dcc.Graph(
        id='test_graph'
    )
])

@app.callback(
    Output('test_graph', 'figure'),
    Input('graph_ma', 'value'))




def callback_a(x):
    fig = go.Figure()
    temp=cov_pos
    print(x)
    temp[str(x)+" Moving avarge"]= temp["corona_result"].rolling(window=x).mean()
    print(temp)
    fig.add_trace(go.Bar(
        x=temp.index,
        y=temp["corona_result"], name="bars"))
    fig.add_trace(go.Scatter(
        x=temp.index,
        y=temp["corona_result"], name="CovidPositive", mode="lines"))
    fig.add_trace(go.Scatter(
        x=temp.index,
        y=temp[(str(x) + "D Moving avarge")], name=(str(x) + " Moving avarge"), mode="lines"))
    return fig





if __name__ == '__main__':
    app.run_server()