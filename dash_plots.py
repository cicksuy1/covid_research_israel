
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
        self.daily_covid_positive_saved = self.make_daily_covid_positive_saved()
        self.saved_ma_list= []


    def make_daily_covid_positive_saved(self):
        temp  = self.daily_covid_positive.copy(deep=False)
        temp.rename(columns={'corona_result':'Covid-19 Positive results'}, inplace=True)
        return temp

    #Reading and manipulating the Covid-19 result lab data from csv
    def covid_pd_make(self):
        return database_to_pandas()

    '''In this function we are reading and making database from info.data.gov.il about the corona test lab result
        From the api we getting the result in json and inside the json string in csv format.
        used query parameters: limit,get_total,resource_id,total_records,records_format
        read more how to execute api quary :https://docs.ckan.org/en/latest/maintaining/datastore.html#ckanext.datastore.logic.action.datastore_search
    '''
    def covid_pd_make_gov_api(self):

        # gov api resource code to corona lab test results
        resource_id = 'dcf999c1-d394-4b57-a5e0-9d014a62e046'
        limit = 0
        get_total = "True"
        records_format ="csv"
        #here we get by quary the total records of covids_test results
        url = "https://data.gov.il/api/3/action/datastore_search?resource_id={}&include_total={}&limit={}".format(resource_id,get_total, limit)
        response = requests.get(url)
        response_json = response.json()
        total_records = response_json['result']["total"]

        #here we genererate all the values from the json csv
        url = "https://data.gov.il/api/3/action/datastore_search?resource_id={}&limit={}&records_format={}".format(
            resource_id, total_records,records_format)
        response = requests.get(url)
        response_json = response.json()
        records = response_json['result']['records']

        #Making csv readable for pandas dataframe
        data = StringIO(records)
        df = pd.read_csv(data, sep=",", names=["_id", "test_date", "result_date", "corona_result", "lab_id",
                                                   "test_for_corona_diagnosis", "is_first_Test"])

        ## here we cuts and manipuilating the data
        df.drop(["_id"], axis=1, inplace=True)
        #result_date is the only persist date colnum so we set it as datetime index
        df.index = pd.DatetimeIndex(df["result_date"])
        df.drop(["result_date"], axis=1, inplace=True)
        df["corona_result"][df["corona_result"] == "שלילי"] = 0
        df["corona_result"][df["corona_result"] == "חיובי"] = 1
        df["is_first_Test"][df["is_first_Test"] == "Yes"] = 1
        df["is_first_Test"][df["is_first_Test"] == "No"] = 0
        return df


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
    def interactive_plot_ma(self,ma=7,to_save_axis= False):
        self.reset_figure()
        fig = None
        if not (to_save_axis):
            print("not Saving")
            self.daily_covid_positive_saved[str(ma) + "D Moving average"] = self.daily_covid_positive_saved[
                "Covid-19 Positive results"].rolling(window=ma).mean()
            fig = self.daily_covid_positive_saved.plot(width=1200, height=700)
            if not (str(ma) + "D Moving average") in self.saved_ma_list:
                self.daily_covid_positive_saved.drop([(str(ma) + "D Moving average")], axis=1, inplace=True)
        else:
            print("Saving")
            self.daily_covid_positive_saved[str(ma) + "D Moving average"] = self.daily_covid_positive_saved[
                "Covid-19 Positive results"].rolling(window=ma).mean()
            fig = self.daily_covid_positive_saved.plot(width=1200, height=700)
            if not (str(ma) + "D Moving average") in self.saved_ma_list:
                self.saved_ma_list.append((str(ma) + "D Moving average"))
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
