import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import plotly
import json

import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import StringIO
pd.options.plotting.backend = "plotly"

class globalvars_class:
    def __init__(self):
        self.covid_df = self.covid_pd_make()
        self.covid_positive = self.covid_positive_frame()
        self.database_date = self.updated_to()
        self.daily_covid_positive = self.covid_positive.groupby(self.covid_positive.index).sum()
        self.daily_covid_positive_saved = self.daily_covid_positive.copy(deep=False)
        self.saved_ma_list= []
    def daily_covid_positive(self):
        return self.daily_covid_positive

    def covid_pd_make(self):
        csv_lab = pd.read_csv("corona_lab_tests_ver_0090.csv")
        csv_lab.index = pd.DatetimeIndex(csv_lab["result_date"])
        csv_lab.drop(["result_date"], axis=1, inplace=True)
        csv_lab["corona_result"][csv_lab["corona_result"] == "שלילי"] = 0
        csv_lab["corona_result"][csv_lab["corona_result"] == "חיובי"] = 1
        csv_lab["is_first_Test"][csv_lab["is_first_Test"] == "Yes"] = 1
        csv_lab["is_first_Test"][csv_lab["is_first_Test"] == "No"] = 0
        return csv_lab


    def covid_pd_make_gov_api(self):

        resource_id = 'dcf999c1-d394-4b57-a5e0-9d014a62e046'#gov api resource coroba lab test
        limit = 0
        get_total = "True"
        #here we get by quary the total records of covids_test results
        url = "https://data.gov.il/api/3/action/datastore_search?resource_id={}&include_total={}&limit={}".format(resource_id,get_total, limit)
        response = requests.get(url)
        response_json = response.json()
        total_records = response_json['result']["total"]

        #here we genererate all the values from the json csv
        url = "https://data.gov.il/api/3/action/datastore_search?resource_id={}&limit={}&records_format=csv".format(
            resource_id, total_records)
        response = requests.get(url)
        response_json = response.json()
        records = response_json['result']['records']

        TESTDATA = StringIO(records)

        df = pd.read_csv(TESTDATA, sep=",", names=["_id", "test_date", "result_date", "corona_result", "lab_id",
                                                   "test_for_corona_diagnosis", "is_first_Test"])
        df.drop(["_id"], axis=1, inplace=True)
        ## here we cuts and manipuilating the data


        df.index = pd.DatetimeIndex(df["result_date"])
        df.drop(["result_date"], axis=1, inplace=True)
        df["corona_result"][df["corona_result"] == "שלילי"] = 0
        df["corona_result"][df["corona_result"] == "חיובי"] = 1
        df["is_first_Test"][df["is_first_Test"] == "Yes"] = 1
        df["is_first_Test"][df["is_first_Test"] == "No"] = 0

        return df


    def covid_positive_frame(self):
        temp = self.covid_df[((self.covid_df["corona_result"] == 0) | (self.covid_df["corona_result"] == 1))][
            "corona_result"].to_frame()
        return temp

    def updated_to(self):
        return self.covid_df.index.max().strftime("%d-%m-%y")
    def reset_figure(self):
        fig = go.Figure()
        fig.data = []
    def interactive_plot_ma(self,ma=7,to_save_axis= False):
        self.reset_figure()
        fig = None
        if not (to_save_axis):
            print("not Saving")
            self.daily_covid_positive_saved[str(ma) + "D Moving avarge"] = self.daily_covid_positive_saved[
                "corona_result"].rolling(window=ma).mean()
            fig = self.daily_covid_positive_saved.plot(width=1200, height=700)
            if not (str(ma) + "D Moving avarge") in self.saved_ma_list:
                self.daily_covid_positive_saved.drop([(str(ma) + "D Moving avarge")], axis=1, inplace=True)
            print(self.daily_covid_positive_saved)
        else:
            print("Saving")
            self.daily_covid_positive_saved[str(ma) + "D Moving avarge"] = self.daily_covid_positive_saved[
                "corona_result"].rolling(window=ma).mean()
            fig = self.daily_covid_positive_saved.plot(width=1200, height=700)
            if not (str(ma) + "D Moving avarge") in self.saved_ma_list:
                self.saved_ma_list.append((str(ma) + "D Moving avarge"))
            print(self.daily_covid_positive_saved)
        return fig
    def three_ma(self):
        self.reset_figure()
        temp =  self.daily_covid_positive.copy(deep=False)
        temp["7Days moving avarge"]=temp["corona_result"].rolling(window=7).mean()
        temp["30Days moving avarge"]=temp["corona_result"].rolling(window=30).mean()
        temp["60days moving avarge"]=temp["corona_result"].rolling(window=60).mean()
        return temp.plot()

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
        tempdf["7days moving avarge of positive results"]=self.daily_covid_positive["corona_result"].rolling(window=7).mean().copy(deep=False)
        return tempdf.plot()

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

    def res_quantire(self):
        self.reset_figure()
        fig = make_subplots(rows=1, cols=2)
        tempdf = self.daily_covid_positive.copy(deep=False)
        print(tempdf)
        tempdf["7 days moving avarge"] = tempdf.rolling(window=7).mean()
        #tempdf = pd.concat([tempdf.loc["2020-03-14":"2020-04-30"],tempdf.loc["2020-09-18":"2020-10-13"]])

        first_quantire1= go.Scatter(x=tempdf.loc["2020-03-14":"2020-04-30"].index, y=tempdf.loc["2020-03-14":"2020-04-30"]["corona_result"],name="Covid-19 Positive")

        first_quantire2 = go.Scatter(x=tempdf.loc["2020-03-14":"2020-04-30"].index,
                                     y=tempdf.loc["2020-03-14":"2020-04-30"]["7 days moving avarge"],name="7 days moving avarge")

        second_quantire1 = go.Scatter(x=tempdf.loc["2020-09-18":"2020-10-13"].index, y=tempdf.loc["2020-09-18":"2020-10-13"]["corona_result"],name="Covid-19 Positive")

        second_quantire2 = go.Scatter(x=tempdf.loc["2020-09-18":"2020-10-13"].index,
                                      y=tempdf.loc["2020-09-18":"2020-10-13"]["7 days moving avarge"],name="7 days moving avarge")



        fig.append_trace(first_quantire1, 1, 1)
        fig.append_trace(first_quantire2, 1, 1)
        fig.append_trace(second_quantire1, 1, 2)
        fig.append_trace(second_quantire2, 1, 2)
        return fig

    def static_figs_json(self):
        figs = [self.three_ma(), self.res_first_test_and_pos_ma(), self.res_first_test_and_pos_clean(),
                self.res_quantire()]
        json_graps = []
        for i in figs:
            i.to_json()
            json_graps.append(json.dumps(i, cls=plotly.utils.PlotlyJSONEncoder))
        return json_graps