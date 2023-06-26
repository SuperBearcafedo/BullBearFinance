import csv

import tushare as ts
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

var_version = ts.__version__


def create_csv(csv_path):
    with open(csv_path, "wb") as f:
        csv_write = csv.writer(f)
    return


def get_data(stock_code, start_date, end_date):
    stock_df = pro.daily(ts_code=stock_code, autype="qfq", start_date=start_date, end_date=end_date)
    print(stock_df)
    stock_df.index = pd.to_datetime(stock_df.trade_date)
    #  此处备份全部的数据
    stock_df.sort_index(inplace=True)
    store_path = os.path.join(os.path.join(os.getcwd(), "Bubble"), stock_code + "_Full.csv")
    stock_df.to_csv(store_path)
    #  下面选取会需要的数据返回
    stock_df = stock_df[["open", "high", "low", "close", "vol", "pre_close"]]
    return stock_df


def acquire_stock(stock_code, start_date, end_date):
    stock_df = get_data(stock_code, start_date, end_date)
    print(stock_df.info())
    print("*" * 100)
    print(stock_df.describe())
    stock_df.sort_index(inplace=True)
    store_path = os.path.join(os.path.join(os.getcwd(), "Bubble"), stock_code + ".csv")
    store_path_exist_flag = os.path.exists(store_path)
    if not store_path_exist_flag:
        create_csv(store_path)
    stock_df.to_csv(store_path)


def read_data_func(store_path):
    store_path_exist_flag = os.path.exists(store_path)
    if not store_path_exist_flag:
        raise Exception("缺乏个股数据源文件，请检查后重新读取")
    stock_info = pd.read_csv(store_path, sep=",", header=0)
    stock_data = pd.DataFrame(stock_info)
    return stock_data


if __name__ == '__main__':
    print(var_version)
    my_token = ""
    pro = ts.pro_api(my_token)
    start_date = "20230601"
    end_date = "20230614"
    stock = "600132.SH"
    #  **********下面段代码只在需要重新拉取数据时使用**********
    #  acquire_stock(stock, start_date, end_date)
    #  **********上面段代码只在需要重新拉取数据时使用**********
    store_path = os.path.join(os.path.join(os.getcwd(), "Bubble"), stock + ".csv")
    stock_data = read_data_func(store_path)
    stock_data["diff"] = stock_data["close"].diff()
    stock_data["signal"] = np.where(stock_data["diff"] > 0, 1, 0)
    print(stock_data)

    #  以下代码为根据信号作图的结果
    plt.figure(figsize=(10, 5))
    stock_data["close"].plot(linewidth=2, color="k", grid=True)
    plt.scatter(stock_data["close"].loc[stock_data.signal == 1].index, stock_data["close"][stock_data.signal == 1],
                marker="v", s=80, c="g")
    plt.scatter(stock_data["close"].loc[stock_data.signal == 0].index, stock_data["close"][stock_data.signal == 0],
                marker="^", s=80, c="r")
    plt.show()
