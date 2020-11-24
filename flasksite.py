from flask import Flask, render_template,request
import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json
from Ploty_Dash_learn.dash_plots import globalvars_class as plotmaker
import plotly.graph_objects as go

app = Flask(__name__)

test= plotmaker()

@app.route("/")
def index():
    return render_template("landing.html")


@app.route("/interact_ma",methods=['GET','POST'])
def interactive_graph():
    ma = int(request.form.get("ma", 7))
    fig=None
    if request.form.get('save') == "on":
        fig = test.interactive_plot_ma(ma=ma,to_save_axis=True)
    else:
        fig = test.interactive_plot_ma(ma=ma, to_save_axis=False)
    fig.to_json()
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("inter_ma.html",plot=graphJSON)

@app.route("/research")
def three_ma_plots():

    figs= [test.three_ma(),test.res_first_test_and_pos_ma(),test.res_first_test_and_pos_clean(),test.res_quantire()]
    json_graps=[]
    for i in figs:
        i.to_json()
        json_graps.append(json.dumps(i, cls=plotly.utils.PlotlyJSONEncoder))

    return render_template("research.html",three_ma=json_graps[0],res_plot_first_test=json_graps[1],res_plot_first_test_positive=json_graps[2],res_quantire=json_graps[3])






if __name__ == '__main__':
    app.run()
