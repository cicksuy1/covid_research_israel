
from flask import Flask, render_template,request,session
import plotly
import json
from dash_plots import globalvars_class as plotmaker
from flask_sqlalchemy  import SQLAlchemy
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = "testing"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///session.sqlite3'
app.config['SESSION_TYPE'] = 'sqlalchemy'

sessdb= SQLAlchemy(app)

app.config['SESSION_SQLALCHEMY'] = sessdb

sess = Session(app)

#sessdb.create_all()


ploter= plotmaker()
static_figs = ploter.static_figs_json()







@app.route("/")
def index():
    return render_template("landing.html")





@app.route("/interact_ma",methods=['GET','POST'])
def interactive_graph():
    #ma is a shortcut for Moving average

    if request.form.get('reset'):
        session["UserSes"] = []
        print("Session Is empty")
    if session.get('UserSes') is None:
        session["UserSes"] = []
        print("Session Is empty")
    by_accsidend=False
    fig = None
    try:
        ma = int(request.form.get("ma", 7))
    except:
        by_accsidend = True
        ma=7
    if request.form.get('save') == "on":
        if not by_accsidend:
            if ma not in  session["UserSes"]:
                session["UserSes"].append(ma)
            fig = ploter.interactive_plot_ma(ma=session["UserSes"], to_save_axis=True)
        else:
            fig = ploter.interactive_plot_ma(ma=session["UserSes"], to_save_axis=False)
    else:

        fig = ploter.interactive_plot_ma(ma=session["UserSes"]+[ma], to_save_axis=False)
    fig.to_json()

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("inter_ma.html",database_date=ploter.database_date,plot=graphJSON)




@app.route("/research")
def static_plots():
    return render_template("research.html",three_ma=static_figs[0],res_plot_first_test=static_figs[1],res_plot_first_test_positive=static_figs[2],res_quantire=static_figs[3])



app.run()


