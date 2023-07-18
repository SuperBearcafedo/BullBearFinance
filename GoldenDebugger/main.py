import csv

import tushare as ts
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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
    my_token = "d93f7a985bb9c8497adaca789293c480f15faa38ef3e12e9fc565278"
    pro = ts.pro_api(my_token)
    start_date = "20220101"
    end_date = "20230701"
    stock = "600132.SH"
    # stock = "600600.SH"
    #  **********下面段代码只在需要重新拉取数据时使用**********
    acquire_stock(stock, start_date, end_date)
    #  **********上面段代码只在需要重新拉取数据时使用**********
    store_path = os.path.join(os.path.join(os.getcwd(), "Bubble"), stock + ".csv")
    stock_data = read_data_func(store_path)
    stock_data["diff"] = stock_data["close"].diff()
    stock_data["signal"] = np.where(stock_data["diff"] > 0, 1, 0)
    #print(stock_data)

    #  以下代码为根据信号作图的结果
    # plt.figure(figsize=(10, 5))
    # stock_data["close"].plot(linewidth=2, color="k", grid=True)
    # plt.scatter(stock_data["close"].loc[stock_data.signal == 1].index, stock_data["close"][stock_data.signal == 1],
    #             marker="v", s=80, c="g")
    # plt.scatter(stock_data["close"].loc[stock_data.signal == 0].index, stock_data["close"][stock_data.signal == 0],
    #             marker="^", s=80, c="r")
    # plt.show()

    # #  下面尝试使用调整后收盘价作为信号
    # zgpa_signal = pd.DataFrame(index=stock_data.index)
    # zgpa_signal["price"] = stock_data["pre_close"]  # 赋予收盘前价格为股票价格
    # zgpa_signal["diff"] = stock_data["pre_close"].diff()  # 计算每天的价差
    # #  下面粗略求取指定天数的均值 以10为例
    # stock_data_series = pd.Series(zgpa_signal["price"])
    # window_size = 10
    # windows = stock_data_series.rolling(window_size)
    # moving_average = windows.mean()
    # moving_average_list = moving_average.tolist()
    # final_moving_average = moving_average_list[:]
    # zgpa_signal["10MA"] = final_moving_average
    # zgpa_signal["10MA"] = zgpa_signal["10MA"].fillna(zgpa_signal["price"].mean())
    # #  下面形成购买购出信号
    # zgpa_signal["signal"] = np.where(zgpa_signal["diff"] >= 0, 1, 0)  # 当第二天涨价，信号为1，否则为0
    # #  进一步要求信号大于指定均线，才能为1，否则为0
    # zgpa_signal["signal2"] = np.where(zgpa_signal["price"] > zgpa_signal["10MA"], 1, 0)
    # zgpa_signal["signal3"] = zgpa_signal["signal"] * zgpa_signal["signal2"]
    # print(zgpa_signal["signal3"])
    # zgpa_signal = zgpa_signal.fillna(0.0)  # 将NaN设置为0
    # zgpa_signal["order"] = zgpa_signal["signal3"].diff() * 100  # 一手来进行计量 100股
    # # 下面计算买的数量根据强度来进行
    # zgpa_signal["power"] = zgpa_signal["price"] / zgpa_signal["10MA"]
    # zgpa_signal["order"] = zgpa_signal["order"] * zgpa_signal["power"]
    # zgpa_signal.head()
    #
    # #  下面对上述策略进行回测
    # initial_cash = 200000.00
    # zgpa_signal["stock"] = zgpa_signal["order"]*zgpa_signal["price"]  # 交易股票的市值
    # zgpa_signal["cash"] = initial_cash - (zgpa_signal["order"].diff() * zgpa_signal["price"]).cumsum()
    # zgpa_signal["total"] = zgpa_signal["stock"] + zgpa_signal["cash"]
    #
    # plt.figure(figsize=(10, 6))
    # plt.plot(zgpa_signal["total"]-initial_cash)
    # #plt.plot(zgpa_signal["10MA"], "--", label="10 MA")
    # #plt.plot(zgpa_signal["price"], "+", label="stock price")
    # #plt.plot(zgpa_signal["order"].cumsum() * zgpa_signal["price"], "--", label="stock value")
    # plt.grid()
    # plt.legend(loc="center right")
    # plt.show()
