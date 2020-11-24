from flask import Flask, render_template,request
import plotly

import json
from Ploty_Dash_learn.dash_plots import globalvars_class as plotmaker


app = Flask(__name__)

ploter= plotmaker()
static_figs = ploter.static_figs_json()





@app.route("/")
def index():
    return render_template("landing.html")


@app.route("/interact_ma",methods=['GET','POST'])
def interactive_graph():
    by_accsidend=False
    fig = None
    try:
        ma = int(request.form.get("ma", 7))
    except:
        by_accsidend = True
        ma=7

    if request.form.get('save') == "on":
        if not by_accsidend:
            fig = ploter.interactive_plot_ma(ma=ma,to_save_axis=True)
        else:
            fig = ploter.interactive_plot_ma(ma=ma, to_save_axis=False)
    else:
        fig = ploter.interactive_plot_ma(ma=ma, to_save_axis=False)
    fig.to_json()
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("inter_ma.html",database_date=ploter.database_date,plot=graphJSON)




@app.route("/research")
def static_plots():
    return render_template("research.html",three_ma=static_figs[0],res_plot_first_test=static_figs[1],res_plot_first_test_positive=static_figs[2],res_quantire=static_figs[3])






if __name__ == '__main__':
    app.run()
