
import io
from flask import Flask, Response, request,render_template,url_for
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import pandas as pd

from CovidSite.generate_plots import globalvars_class as data_maker



app = Flask(__name__)

plot_maker = data_maker()

@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/interact_ma")
def interact_page():
    try:
        plot_maker.moving_avarge = int(request.args.get("ma", 7))
    except:
        plot_maker.moving_avarge = 7
    return render_template("emainteractive.html", database_date=plot_maker.database_date, ma=plot_maker.moving_avarge)


#Responsive ma graph
@app.route("/inter_plot.png")
def interact_plot():
    return plot_maker.interact_positive_ema(ma=plot_maker.moving_avarge)


@app.route("/inter_plot_saved.png")
def interact_plot():
    return plot_maker.interact_positive_ema(ma=plot_maker.moving_avarge)




@app.route("/research")
def research():
    return render_template("research.html")



#plotting 3 different ma to a picture
@app.route("/plot_3_ma.png")
def mul_ema_plot():
    return plot_maker.res_plot_3ma()


#plotting positive and first and not first test plot with ma
@app.route("/positive_first_ma.png")
def first_test_pos_ma():
    return plot_maker.res_first_test_and_pos_ema()

#plotting positive and first and not first test plot

@app.route("/positive_first.png")
def first_test_pos():
    return plot_maker.res_first_test_and_pos_clean()



@app.route("/quantire.png")
def quantire_plot():
    return plot_maker.res_quantire()


if __name__ == "__main__":

    import webbrowser
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)