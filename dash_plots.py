
import plotly
import json
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import StringIO
from database_maker import database_to_pandas

#Swiching pandas ploting backend to plotly
pd.options.plotting.backend = "plotly"


class globalvars_class:
    def __init__(self):
        self.covid_df = self.covid_pd_make()
        self.covid_positive = self.covid_positive_frame()
        self.database_date = self.updated_to()
        self.daily_covid_positive = self.covid_positive.groupby(self.covid_positive.index).sum()
        self.saved_ma_list= []



    #Reading and manipulating the Covid-19 result lab data from database
    def covid_pd_make(self):
        return database_to_pandas()

    #Making Covid-19 positive results as individual dataframe
    def covid_positive_frame(self):
        temp = self.covid_df[((self.covid_df["corona_result"] == 0) | (self.covid_df["corona_result"] == 1))][
            "corona_result"].to_frame()
        return temp

    #Taking the last date index in the dataframe and returt it as string
    def updated_to(self):
        return self.covid_df.index.max().strftime("%d-%m-%y")

    #Restarting the plotly figure data
    def reset_figure(self):
        fig = go.Figure()
        fig.data = []

    '''This function making a plot of positive results with the desired moving average.
    receiving: ma = desired moving average , to_save_axis = will be true if the user want to save the plot'''

    def interactive_plot_ma(self,ma=[7],to_save_axis= False):
        self.reset_figure()
        fig = None
        tempdf = self.daily_covid_positive.copy(deep=False)
        tempdf.rename(columns={'corona_result': 'Covid-19 Positive results'}, inplace=True)

        for i in ma:
            tempdf[str(i) + "D Moving average"] = tempdf['Covid-19 Positive results'].rolling(window=i).mean()

        fig = tempdf.plot(width=1200, height=700)
        return fig


    #plotting 3 moving average and returning the plot
    def three_ma(self):
        self.reset_figure()
        temp =  self.daily_covid_positive.copy(deep=False)
        temp["7Days moving average"]=temp["corona_result"].rolling(window=7).mean()
        temp["30Days moving average"]=temp["corona_result"].rolling(window=30).mean()
        temp["60days moving average"]=temp["corona_result"].rolling(window=60).mean()
        return temp.plot()

    #plotting tests per day with positive results per day and 7 days moving average on positive results
    def res_first_test_and_pos_ma(self):
        self.reset_figure()
        tempdf = pd.DataFrame()
        first_test = self.covid_df[self.covid_df["is_first_Test"] == 1].copy(deep=False)
        another_test = self.covid_df[self.covid_df["is_first_Test"] == 0].copy(deep=False)
        first_test.drop(["test_date"], axis=1, inplace=True)
        another_test.drop(["test_date"], axis=1, inplace=True)
        tempdf["First test per day"]= first_test["is_first_Test"].groupby(first_test.index).size().copy(deep=False)
        tempdf["Not First test per day"]= another_test["is_first_Test"].groupby(another_test.index).size().copy(deep=False)
        tempdf["Covid-19 posotive results"]=self.daily_covid_positive["corona_result"].copy(deep=False)
        tempdf["7days moving average of positive results"]=self.daily_covid_positive["corona_result"].rolling(window=7).mean().copy(deep=False)
        return tempdf.plot()

    #plotting positive test results to covid-19 with positive results per day
    def res_first_test_and_pos_clean(self):
        self.reset_figure()
        tempdf = pd.DataFrame()
        first_test_pos = self.covid_df[
            (self.covid_df["is_first_Test"] == 1) & (self.covid_df["corona_result"] == 1)].copy(deep=False)
        other_test_pos = self.covid_df[
            (self.covid_df["is_first_Test"] == 0) & (self.covid_df["corona_result"] == 1)].copy(deep=False)
        tempdf["first test positive"] = first_test_pos["corona_result"].groupby(first_test_pos.index).sum()
        tempdf["Not first test positive "] = other_test_pos["corona_result"].groupby(other_test_pos.index).sum()
        tempdf["Covid-19 posotive results"] = self.daily_covid_positive["corona_result"].copy(deep=False)
        self.res_quantire()
        return tempdf.plot()

#ploting the quantire times 2020-03-14-2020-04-30 , 2020-09-18-2020-10-13 with 7 days moving average period
    def res_quantire(self):
        self.reset_figure()
        fig = make_subplots(rows=1, cols=2)
        tempdf = self.daily_covid_positive.copy(deep=False)
        tempdf["7 days moving average"] = tempdf.rolling(window=7).mean()

        first_quantire1= go.Scatter(x=tempdf.loc["2020-03-14":"2020-05-29"].index, y=tempdf.loc["2020-03-14":"2020-05-29"]["corona_result"],name="Covid-19 Positive")
        first_quantire2 = go.Scatter(x=tempdf.loc["2020-03-14":"2020-05-29"].index,
                                     y=tempdf.loc["2020-03-14":"2020-05-29"]["7 days moving average"],name="7 days moving average")
        second_quantire1 = go.Scatter(x=tempdf.loc["2020-09-18":"2020-10-13"].index, y=tempdf.loc["2020-09-18":"2020-10-13"]["corona_result"],name="Covid-19 Positive")
        second_quantire2 = go.Scatter(x=tempdf.loc["2020-09-18":"2020-10-13"].index,
                                      y=tempdf.loc["2020-09-18":"2020-10-13"]["7 days moving average"],name="7 days moving average")


        fig.append_trace(first_quantire1, 1, 1)
        fig.append_trace(first_quantire2, 1, 1)
        fig.append_trace(second_quantire1, 1, 2)
        fig.append_trace(second_quantire2, 1, 2)
        return fig
    #Here we generate the 4 figures to a json graphs.
    def static_figs_json(self):
        figs = [self.three_ma(), self.res_first_test_and_pos_ma(), self.res_first_test_and_pos_clean(),
                self.res_quantire()]
        json_graps = []
        for i in figs:
            i.to_json()
            json_graps.append(json.dumps(i, cls=plotly.utils.PlotlyJSONEncoder))
        return json_graps
