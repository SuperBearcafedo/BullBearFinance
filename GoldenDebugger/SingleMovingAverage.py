import csv

import tushare as ts
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
var_version = ts.__version__
from main import read_data_func, acquire_stock


if __name__ == '__main__':
    print(var_version)
    my_token = ""
    pro = ts.pro_api(my_token)
    start_date = "20220101"
    end_date = "20230626"
    #stock = "600600.SH"  # 选择股票为青岛啤酒
    stock = "600132.SH"  # 选择股票为重庆啤酒
    #  **********下面段代码只在需要重新拉取数据时使用**********
    # acquire_stock(stock, start_date, end_date)
    #  **********上面段代码只在需要重新拉取数据时使用**********
    store_path = os.path.join(os.path.join(os.getcwd(), "Bubble"), stock + ".csv")
    stock_data = read_data_func(store_path)
    stock_data["diff"] = stock_data["close"].diff()
    stock_data["signal"] = np.where(stock_data["diff"] > 0, 1, 0)

    # 单M日均线移动平均策略Single Moving Average
    period = 10
    period_prices = []  # 用于存储period期间的价格
    avg_period_prices = []  # 用于存储period期间的平均价格
    stock_all_information = pd.DataFrame(index=stock_data.index)  # 将读取到的数据全部转化为pandas格式
    stock_all_information["price"] = stock_data["pre_close"]  # 赋予收盘前价格为股票价格
    for price in stock_all_information["price"]:
        period_prices.append(price)  # 存入每日价格到列表
        if len(period_prices) > period:
            del period_prices[0]  # 如果列表长度大于period，删除直至保留period天数数据
        avg_period_prices.append(np.mean(period_prices))  # 求取平均价格，并存入列表
    # 将stock_all_information改为价格和均价的pd.DataFrame
    stock_all_information = stock_all_information.assign(avg_period_prices=pd.Series(avg_period_prices, index=stock_all_information.index))
    # 绘制股价和均价的曲线图
    # plt.figure(figsize=(10,6))
    # plt.plot(stock_all_information["price"], lw=2, c="k")  # 股价变化趋势图
    # plt.plot(stock_all_information["avg_period_prices"], "--", lw=2, c="b") # 股价均线趋势
    # plt.legend()
    # plt.grid()
    # plt.show()

    # 下面进行双均线策略
    double_line_strategy = pd.DataFrame(index=stock_all_information.index)
    double_line_strategy["price"] = stock_all_information["price"]  # 赋予股价
    double_line_strategy["signal"] = 0  # 该信号用于存储交易信号
    # 分别计算5日均线和10日均线的值 --> 调试发现15日和25日均线效果较为理想【青岛啤酒】
    double_line_strategy["avg_5"] = stock_all_information["price"].rolling(5).mean()
    double_line_strategy["avg_10"] = stock_all_information["price"].rolling(10).mean()
    # 原理是：当5日均线突破10均线，说明短期内具有更强烈的上冲动量，能冲破时，将信号设置为1，从0到1代表买入；否则为0，从1到0卖出
    double_line_strategy["signal"] = np.where(double_line_strategy["avg_5"] > double_line_strategy["avg_10"], 1, 0)
    double_line_strategy["strength"] = double_line_strategy["avg_5"]/double_line_strategy["avg_10"]  # 买卖量根据强度决定
    double_line_strategy["order"] = double_line_strategy["signal"].diff()  # 得到买卖信号

    # 下面绘制双均线趋势图
    # plt.figure(figsize=(10, 6))
    # plt.plot(double_line_strategy["price"], lw=2, c="k", label="price")  # 股价变化趋势图
    # plt.plot(double_line_strategy["avg_5"], "--", lw=2, c="b", label="average_5days")  # 5日股价均线趋势
    # plt.plot(double_line_strategy["avg_10"], "-.", lw=2, c="r", label="average_10days")  # 10日股价均线趋势
    # plt.scatter(double_line_strategy["price"].loc[double_line_strategy.order==1].index,
    #             double_line_strategy["price"][double_line_strategy.order==1], marker="^", s=80, color="r", label="BUY")
    # plt.scatter(double_line_strategy["price"].loc[double_line_strategy.order == -1].index,
    #             double_line_strategy["price"][double_line_strategy.order == -1], marker="v", s=80, color="g",
    #             label="SELL")
    # plt.legend()
    # plt.grid()
    # plt.show()

    # 下面对双均线进行回测
    initial_cash = 20000
    portfolio = pd.DataFrame(index=double_line_strategy.index).fillna(0)
    portfolio["price"] = double_line_strategy["price"]
    portfolio["stockNum"] = double_line_strategy["signal"] * 100  # 100股为1手，设置买入数量
    portfolio["stockValue"] = portfolio["price"] * portfolio["stockNum"]  # 购买消耗的现金
    portfolio["order"] = portfolio["stockNum"].diff()
    portfolio["cash"] = initial_cash - (portfolio["price"] * portfolio["order"]).cumsum()
    portfolio["total"] = portfolio["cash"] + portfolio["stockValue"]
    print(portfolio)
    plt.figure(figsize=(10, 6))
    plt.plot(portfolio["total"], lw=2, c="k", label="Total")  # 总资产价值
    plt.plot(portfolio["stockValue"], "--", lw=2, c="b", label="StockValue") # 股票价值
    plt.legend()
    plt.grid()
    plt.show()





