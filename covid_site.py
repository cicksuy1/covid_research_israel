
import io
from flask import Flask, Response, request,render_template,url_for
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import pandas as pd



app = Flask(__name__)

class globalvars_class:
    def __init__(self):
        self.moving_avarge=7
        self.covid_df = self.covid_pd_make()
        self.covid_positive = self.covid_positive_frame()
        self.database_date = self.updated_to()
        self.daily_covid_positive = self.covid_positive.groupby(self.covid_positive.index).sum()
    #functions
    def covid_pd_make(self):
        csv_lab = pd.read_csv("corona_lab_tests_ver_0090.csv")
        csv_lab.index = pd.DatetimeIndex(csv_lab["result_date"])
        csv_lab.drop(["result_date"], axis=1, inplace=True)
        csv_lab["corona_result"][csv_lab["corona_result"] == "שלילי"] = 0
        csv_lab["corona_result"][csv_lab["corona_result"] == "חיובי"] = 1
        csv_lab["is_first_Test"][csv_lab["is_first_Test"] == "Yes"] = 1
        csv_lab["is_first_Test"][csv_lab["is_first_Test"] == "No"] = 0
        return csv_lab
    def covid_positive_frame(self):
        temp = self.covid_df[((self.covid_df["corona_result"] == 0) | (self.covid_df["corona_result"] == 1))][
            "corona_result"].to_frame()
        return temp
    def updated_to(self):
        return self.covid_df.index.max().strftime("%d-%m-%y")

globalvars = globalvars_class()

def plot_to_img(fig):
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")

def interact_positive_ema(ma):
    fig = plt.figure(figsize=(16, 10))
    covid_positive = globalvars.covid_positive
    covid_positive = covid_positive.groupby(covid_positive.index).sum()
    covid_positive["corona_result"].plot(label="Corona positive results per day", figsize=(16, 10))
    covid_positive["corona_result"].rolling(window=ma).mean().plot(alpha=0.8, label=str(ma) + "MA")
    plt.legend()
    return plot_to_img(fig)


def res_plot_3ma():
    fig = plt.figure(figsize=(16, 10))
    daily_covid_positive = globalvars.covid_positive.groupby(globalvars.covid_positive.index).sum()
    daily_covid_positive["corona_result"].plot(label="Corona positive results")
    daily_covid_positive["corona_result"].rolling(window=7).mean().plot(alpha=0.8, label="7MA")
    daily_covid_positive["corona_result"].rolling(window=30).mean().plot(alpha=0.8, label="30MA")
    daily_covid_positive["corona_result"].rolling(window=60).mean().plot(alpha=0.8, label="60MA")
    plt.legend()
    return plot_to_img(fig)

def res_first_test_and_pos_ema():

    fig = plt.figure(figsize=(16, 10))
    first_test = globalvars.covid_df[globalvars.covid_df["is_first_Test"] == 1]
    another_test = globalvars.covid_df[globalvars.covid_df["is_first_Test"] == 0]


    first_test.drop(["test_date"], axis=1, inplace=True)
    another_test.drop(["test_date"], axis=1, inplace=True)

    first_test["is_first_Test"].groupby(first_test.index).size().plot(label="First test")

    another_test["is_first_Test"].groupby(another_test.index).size().plot(label="Not First test")

    globalvars.daily_covid_positive["corona_result"].plot(label="positive").plot()
    globalvars.daily_covid_positive["corona_result"].rolling(window=7).mean().plot(alpha=0.8, label="7MA")


    plt.legend()
    return plot_to_img(fig)

def res_first_test_and_pos_clean():
    fig = plt.figure(figsize=(16, 10))
    first_test = globalvars.covid_df[(globalvars.covid_df["is_first_Test"] == 1) & (globalvars.covid_df["corona_result"] == 1)]
    other_test = globalvars.covid_df[(globalvars.covid_df["is_first_Test"] == 0) & (globalvars.covid_df["corona_result"] == 1)]
    first_test["corona_result"].groupby(first_test.index).sum().plot(label="first test")
    other_test["corona_result"].groupby(other_test.index).sum().plot(label="Not first test")
    globalvars.covid_positive["corona_result"].plot(label="positive").plot()
    plt.legend()
    return plot_to_img(fig)

def res_quantire():
    fig = plt.figure(figsize=(16, 10))
    globalvars.covid_positive["7MA"] = globalvars.covid_positive.rolling(window=7).mean()
    globalvars.covid_positive.loc["2020-03-14":"2020-04-30"].plot()
    globalvars.covid_positive.loc["2020-09-18":"2020-10-13"].plot()
    plt.legend()
    return plot_to_img(fig)



@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/interact_ma")
def interact_page():
    try:
        globalvars.moving_avarge = int(request.args.get("ma", 7))
    except:
        globalvars.moving_avarge = 7
    return render_template("emainteractive.html", database_date=globalvars.database_date, ma=globalvars.moving_avarge)


#Responsive ma graph
@app.route("/inter_plot.png")
def interact_plot():
    return interact_positive_ema(ma=globalvars.moving_avarge)





@app.route("/research")
def research():
    return render_template("research.html")



#plotting 3 different ma to a picture
@app.route("/plot_3_ma.png")
def mul_ema_plot():
    return res_plot_3ma()


#plotting positive and first and not first test plot with ma
@app.route("/positive_first_ma.png")
def first_test_pos_ma():
    return res_first_test_and_pos_ema()

#plotting positive and first and not first test plot

@app.route("/positive_first.png")
def first_test_pos():
    return res_first_test_and_pos_clean()


@app.route("/quantire.png")
def quantire_plot():
    return res_quantire()


if __name__ == "__main__":

    import webbrowser
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)