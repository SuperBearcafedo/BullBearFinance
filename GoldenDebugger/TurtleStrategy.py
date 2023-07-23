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
    my_token = "d93f7a985bb9c8497adaca789293c480f15faa38ef3e12e9fc565278"
    pro = ts.pro_api(my_token)
    start_date = "20220101"
    end_date = "20230626"
    # stock = "600600.SH"  # 选择股票为青岛啤酒
    stock = "600132.SH"  # 选择股票为重庆啤酒
    #  **********下面段代码只在需要重新拉取数据时使用**********
    # acquire_stock(stock, start_date, end_date)
    #  **********上面段代码只在需要重新拉取数据时使用**********
    store_path = os.path.join(os.path.join(os.getcwd(), "Bubble"), stock + ".csv")
    stock_data = read_data_func(store_path)
    stock_data["diff"] = stock_data["close"].diff()
    stock_data["signal"] = np.where(stock_data["diff"] > 0, 1, 0)

    turtle = pd.DataFrame(index=stock_data.index)
    period = 5
    turtle['high'] = stock_data['close'].shift(1).rolling(period).max()  # 寻找period期间的最大值
    turtle['low'] = stock_data['close'].shift(1).rolling(period).min()  # 寻找period期间的最小值
    turtle['buy'] = stock_data['close'] > turtle['high']
    turtle['sell'] = stock_data['close'] < turtle['low']

    turtle['orders'] = 0
    position = 0
    for k in range(len(turtle)):
        if turtle.buy[k] and position == 0:
            turtle.orders.values[k] = 1
            position = 1
        elif turtle.sell[k] and position > 0:
            turtle.orders.values[k] = -1
            position = 0

    # 下面绘制海龟策略
    # plt.figure(figsize=(10, 6))
    # plt.plot(stock_data["close"], lw=2)
    # plt.plot(turtle['high'], lw=2, ls="--", c='r')
    # plt.plot(turtle['low'], lw=2, ls="--", c='g')
    # plt.scatter(turtle.loc[turtle.orders==1].index, stock_data['close'][turtle.orders==1], marker="^", s=80, color='r', label='Buy')
    # plt.scatter(turtle.loc[turtle.orders == -1].index, stock_data['close'][turtle.orders == -1], marker="v", s=80, color='g', label='Sell')
    # plt.legend()
    # plt.grid()
    # plt.show()

    initial_cash = 20000
    positions = pd.DataFrame(index=turtle.index).fillna(0.0)
    positions['stock'] = 100 * turtle['orders'].cumsum()
    portfolio = positions.multiply(stock_data['close'], axis=0)
    portfolio["holding_values"] = (positions.multiply(stock_data["close"], axis=0))
    pos_diff = positions.diff()
    portfolio['cash'] = initial_cash - (pos_diff.multiply(stock_data['close'], axis=0)).cumsum()
    portfolio["total"] = portfolio["cash"] + portfolio["holding_values"]

    # 下面对海龟策略进行回测
    plt.figure(figsize=(10, 6))
    plt.plot(portfolio["total"])
    plt.plot(portfolio["holding_values"], "--")
    plt.grid()
    plt.legend()
    plt.show()
