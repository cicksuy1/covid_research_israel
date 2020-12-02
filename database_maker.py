

import sqlite3
import requests
from alive_progress import alive_bar
import urllib.request as rr
from pathlib import Path


import pandas as pd


def create_table():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c1 = c.execute('PRAGMA encoding="UTF-8";')
    c.execute(
        '''CREATE TABLE covid_data( _id int, test_date text, result_date text,corona_result TEXT,lab_id int,test_for_corona_diagnosis int,is_first_Test text)''')
    conn.commit()

def drop_data():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DROP TABLE covid_data")
    conn.commit()


def insert_records(records):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c1 = c.execute('PRAGMA encoding="UTF-8";')
    print("starting to make")
    records = records.splitlines()
    with alive_bar(len(records)) as bar:
            for i in records:
                i = i.split(',')
                sql = '''INSERT INTO covid_data(_id,test_date,result_date,corona_result,
                        lab_id,test_for_corona_diagnosis,is_first_Test) VALUES({},'{}','{}','{}',{},{},'{}')'''.format(i[0],i[1],i[2],i[3],i[4],i[5],i[6])
                c1.execute(sql)
                bar()

    conn.commit()


def get_total_api_records():
    resource_id = 'dcf999c1-d394-4b57-a5e0-9d014a62e046'
    limit = 0
    get_total = "True"
    # here we get by quary the total records of covids_test results
    url = "https://data.gov.il/api/3/action/datastore_search?resource_id={}&include_total={}&limit={}".format(
        resource_id,
        get_total,
        limit)
    response = requests.get(url)
    response_json = response.json()
    return response_json['result']["total"]


def create_database():

    Path('database.db').touch()
    resource_id = 'dcf999c1-d394-4b57-a5e0-9d014a62e046'
    records_format = "csv"
    total_records = get_total_api_records()

    url = "https://data.gov.il/api/3/action/datastore_search?resource_id={}&limit={}&records_format={}".format(
            resource_id, total_records,records_format)

    response = requests.get(url)
    response_json = response.json()
    total_records = response_json['result']["records"]
    insert_records(total_records)

def database_to_pandas():
    api_update()
    conn = sqlite3.connect('database.db')

    df = pd.read_sql_query("SELECT * from covid_data", conn)


    df.drop(["_id"], axis=1, inplace=True)

    # result_date is the only persist date colnum so we set it as datetime index
    df.drop(df[df["result_date"] == "NULL"].index, inplace=True)
    df.index = pd.DatetimeIndex(df["result_date"])
    df.drop(["result_date"], axis=1, inplace=True)
    df["corona_result"][df["corona_result"] == "שלילי"] = 0
    df["corona_result"][df["corona_result"] == "חיובי"] = 1
    df["is_first_Test"][df["is_first_Test"] == "Yes"] = 1
    df["is_first_Test"][df["is_first_Test"] == "No"] = 0
    return df
    # Verify that result of SQL query is stored in the dataframe

def last_value():
    sql= 'SELECT * FROM covid_data ORDER BY _id DESC LIMIT 1;'
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(sql)
    result_set = c.fetchall()
    return result_set[0][0]

def api_update():
    totat_db_records = last_value()
    new_records = get_total_api_records() - totat_db_records
    resource_id = 'dcf999c1-d394-4b57-a5e0-9d014a62e046'
    records_format= 'csv'
    if new_records>0:
        url = "https://data.gov.il/api/3/action/datastore_search?resource_id={}&offset={}&limit={}&records_format={}".format(
            resource_id,totat_db_records, new_records, records_format)
        response = requests.get(url)
        response_json = response.json()
        total_records = response_json['result']["records"]
        insert_records(total_records)
        print(str(total_records)+"has been added")
    else:
        print("nothing to update")
