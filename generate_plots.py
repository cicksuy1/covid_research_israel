import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import pandas as pd
import time
from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())


class globalvars_class:
    def __init__(self):
        self.moving_avarge=7
        self.covid_df = self.covid_pd_make()
        self.covid_positive = self.covid_positive_frame()
        self.database_date = self.updated_to()
        self.daily_covid_positive = self.covid_positive.groupby(self.covid_positive.index).sum()
        #self.fig = plt.figure(num=1,figsize=(16, 10))
        #self.fig_saved = plt.figure(num=2,figsize=(16, 10))
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




    def reset_figure(self,fig_num=1):
        plt.close(fig=plt.figure(num=fig_num))
        print("succsessfuly closed")
        plt.figure(num=fig_num,figsize=(16,10))



    def plot_to_img(self):
        output = io.BytesIO()
        FigureCanvasAgg(plt.figure(1)).print_png(output)
        self.reset_figure()
        return Response(output.getvalue(), mimetype="image/png")

    def plot_to_img_saved(self):
        output = io.BytesIO()
        FigureCanvasAgg(plt.figure(2)).print_png(output)
        return Response(output.getvalue(), mimetype="image/png")


    def interact_positive_ema(self,ma):
        self.reset_figure()
        covid_positive = self.covid_positive
        covid_positive = covid_positive.groupby(covid_positive.index).sum()
        covid_positive["corona_result"].plot(label="Corona positive results per day", figsize=(16, 10))
        covid_positive["corona_result"].rolling(window=ma).mean().plot(alpha=0.8, label=str(ma) + "MA")
        plt.legend()
        plt.tight_layout()

        return self.plot_to_img()


    def interact_positive_ma_saved(self,ma):
        if plt.fignum_exists(2):
            print("exist")
            covid_positive = self.covid_positive
            covid_positive = covid_positive.groupby(covid_positive.index).sum()
            covid_positive["corona_result"].rolling(window=ma).mean().plot(alpha=0.8, label=str(ma) + "MA")
            plt.legend()
        else:
            print("not exist")
            fig_saved = plt.figure(num=2)
            covid_positive = self.covid_positive
            covid_positive = covid_positive.groupby(covid_positive.index).sum()
            covid_positive["corona_result"].plot(label="Corona positive results per day", figsize=(16, 10))
            covid_positive["corona_result"].rolling(window=ma).mean().plot(alpha=0.8, label=str(ma) + "MA")
            plt.legend()
        plt.tight_layout()
        return self.plot_to_img_saved()


    def res_plot_3ma(self):
        self.reset_figure()
        if plt.fignum_exists(1):
            print("Plotting exist")
        else:
            print("What the fuck")
        print("Plotting1")
        daily_covid_positive = self.covid_positive.groupby(self.covid_positive.index).sum()
        print("daily_covid_positive")
        daily_covid_positive["corona_result"].plot(label="Corona positive results")
        print("Plotting3")
        daily_covid_positive["corona_result"].rolling(window=7).mean().plot(alpha=0.8, label="7MA")
        print("Plotting4")
        daily_covid_positive["corona_result"].rolling(window=30).mean().plot(alpha=0.8, label="30MA")
        print("Plotting5")
        daily_covid_positive["corona_result"].rolling(window=60).mean().plot(alpha=0.8, label="60MA")
        print("Plotting6")
        plt.legend()
        return self.plot_to_img()

    def res_first_test_and_pos_ema(self):
        self.reset_figure()
        first_test = self.covid_df[self.covid_df["is_first_Test"] == 1]
        another_test = self.covid_df[self.covid_df["is_first_Test"] == 0]
        first_test.drop(["test_date"], axis=1, inplace=True)
        another_test.drop(["test_date"], axis=1, inplace=True)
        first_test["is_first_Test"].groupby(first_test.index).size().plot(label="First test")
        another_test["is_first_Test"].groupby(another_test.index).size().plot(label="Not First test")
        self.daily_covid_positive["corona_result"].plot(label="positive").plot()
        self.daily_covid_positive["corona_result"].rolling(window=7).mean().plot(alpha=0.8, label="7MA")
        plt.legend()
        return self.plot_to_img()

    def res_first_test_and_pos_clean(self):
        self.reset_figure()
        first_test = self.covid_df[
            (self.covid_df["is_first_Test"] == 1) & (self.covid_df["corona_result"] == 1)]
        other_test = self.covid_df[
            (self.covid_df["is_first_Test"] == 0) & (self.covid_df["corona_result"] == 1)]
        first_test["corona_result"].groupby(first_test.index).sum().plot(label="first test")
        other_test["corona_result"].groupby(other_test.index).sum().plot(label="Not first test")
        self.covid_positive["corona_result"].plot(label="positive").plot()
        plt.legend()
        return self.plot_to_img()

    def res_quantire(self):
        self.reset_figure()
        self.covid_positive["7MA"] = self.covid_positive.rolling(window=7).mean()
        self.covid_positive.loc["2020-03-14":"2020-04-30"].plot()
        self.covid_positive.loc["2020-09-18":"2020-10-13"].plot()
        plt.legend()
        return self.plot_to_img()

