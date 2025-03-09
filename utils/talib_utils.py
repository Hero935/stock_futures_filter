import os
import shutil
import pandas as pd
import numpy as np
from itertools import product
import talib
from utils.signal_utils import SignalEvaluator


def get_ma(data, timeperiod=20):
    ma = talib.MA(data["Close"], timeperiod=timeperiod)
    data[f"MA"] = ma
    return data


def get_macd(data, fastperiod=12, slowperiod=26, signalperiod=9):
    macd, signal, hist = talib.MACD(
        data["Close"],
        fastperiod=fastperiod,
        slowperiod=slowperiod,
        signalperiod=signalperiod,
    )
    """
    macd:DIF
    macd_signal:dea
    macd_hist:macd
    """
    data["MACD"] = macd
    data["MACD_Signal"] = signal
    data["MACD_Hist"] = hist
    return data


def get_rsi(data, timeperiod=14):
    rsi = talib.RSI(data["Close"], timeperiod=timeperiod)
    data["RSI"] = rsi
    return data


def get_willr(data, timeperiod=14):
    willr = talib.WILLR(data["High"], data["Low"], data["Close"], timeperiod=timeperiod)
    data["WILLR"] = willr
    return data


def get_kdj(data, fastk_period=9, slowk_period=3, slowd_period=3):
    # 计算K值和D值
    k, d = talib.STOCH(
        data["High"],
        data["Low"],
        data["Close"],
        fastk_period=fastk_period,  # KDJ中的K值周期通常为9
        slowk_period=slowk_period,
        slowk_matype=0,
        slowd_period=slowd_period,
        slowd_matype=0,
    )
    # 计算J值
    j = talib.SMA(
        (3 * k - 2 * d), timeperiod=3
    )  # J值计算公式为3K-2D，并取3日简单移动平均

    data["K"] = k
    data["D"] = d
    data["J"] = j  # 将J值添加到数据中

    return data


def calculate_indicators(
    ticker,
    data,
    ma_periods,
    rsi_periods,
    macd_params,
    willr_periods,
    kdj_params,
    save_condition=0.8,
):
    """
    根據不同參數計算技術指標
    """
    results = []

    if os.path.exists("data_results"):
        shutil.rmtree("data_results")

    os.makedirs("data_results")

    for ma_period, rsi_period, macd_param, willr_period, kdj_param in product(
        ma_periods, rsi_periods, macd_params, willr_periods, kdj_params
    ):
        temp_data = data.copy()

        # 顯示目前執行的條件
        print(
            f"Processing: MA={ma_period}, RSI={rsi_period}, MACD={macd_param}, WILLR={willr_period}, KDJ={kdj_param}"
        )

        # 計算 MA
        temp_data = get_ma(temp_data, timeperiod=ma_period)

        # 計算 MACD
        fastperiod, slowperiod, signalperiod = macd_param
        temp_data = get_macd(temp_data, fastperiod, slowperiod, signalperiod)

        # 計算 RSI
        temp_data = get_rsi(temp_data, timeperiod=rsi_period)

        # 計算 WILLR
        temp_data = get_willr(temp_data, timeperiod=willr_period)

        # 計算 KDJ
        fastk_period, slowk_period, slowd_period = kdj_param
        temp_data = get_kdj(temp_data, fastk_period, slowk_period, slowd_period)

        # 計算信號和利潤
        temp_data = process_signals(temp_data)
        gross_profit, gross_loss, profit_factor, count = calculate_profit(temp_data)

        # 儲存每組參數的結果
        results.append(
            {
                "MA": ma_period,
                "RSI": rsi_period,
                "MACD": f"({fastperiod},{slowperiod},{signalperiod})",
                "WILLR": willr_period,
                "KDJ": f"({fastk_period},{slowk_period},{slowd_period})",
                "Gross Profit": gross_profit,
                "Gross Loss": gross_loss,
                "Profit Factor": profit_factor,
                "Count": count,
            }
        )

        if profit_factor > save_condition:
            # 儲存每組條件結果到獨立的CSV文件
            filepath_data_results = os.path.join(
                "data_results",
                f"{ticker}_MA({ma_period})_RSI({rsi_period})_MACD({fastperiod},{slowperiod},{signalperiod})_WILLR({willr_period})_KDJ({fastk_period},{slowk_period},{slowd_period}).csv",
            )
            temp_data.to_csv(filepath_data_results, index=False)

    # 儲存綜合結果到CSV
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values("Profit Factor", ascending=False)
    filepath_strategy_results = os.path.join("data", f"{ticker}_strategy_results.csv")
    result_df.to_csv(filepath_strategy_results, index=False)


def process_signals(df):
    """
    根據買賣信號判斷進行交易操作並計算獲利
    """
    bought = False
    buy_price = 0
    buy_date = None

    # 初始化信號欄位
    df["Signal"] = 0
    df["Profit"] = np.nan
    df["Buy Date"] = pd.NaT

    evaluator = SignalEvaluator()

    for i in range(len(df)):
        row = df.iloc[i]

        if evaluator.is_buy_signal(row) and not bought:  # 如果符合買入信號並且尚未買入
            df.at[i, "Signal"] = 1  # 設為買入信號
            buy_price = row["Close"]
            buy_date = row["Date"]
            bought = True  # 設為已經買入
        elif evaluator.is_sell_signal(row) and bought:  # 如果符合賣出信號並且已經買入
            df.at[i, "Signal"] = -1  # 設為賣出信號
            df.at[i, "Profit"] = row["Close"] - buy_price  # 計算賣出-買入
            df.at[i, "Buy Date"] = buy_date  # 記錄買入日期
            bought = False  # 重置為未買入狀態

    return df


def calculate_profit(df):
    """
    計算獲利因子：毛利/毛損
    """
    gross_profit = df[df["Profit"] > 0]["Profit"].sum()  # 只計算毛利，即 Profit > 0
    gross_loss = df[df["Profit"] < 0]["Profit"].sum()  # 只計算毛損，即 Profit < 0
    gross_loss = abs(gross_loss)  # 取毛損的絕對值
    count = df[df["Signal"] == -1]["Profit"].count()

    # 計算獲利因子
    profit_factor = gross_profit / gross_loss if gross_loss != 0 else np.nan

    return gross_profit, gross_loss, profit_factor, count


def _is_buy_signal(row):
    """
    判斷是否符合買入信號
    CLOSE > < MA AND RSI < 30 OR MACD > 0 AND WILLR < -80 OR J < 0
    """
    return (
        (row["Close"] > row["MA"] and row["RSI"] < 30)  # 收盤價高於MA日均線且RSI超賣
        or (row["MACD_Diff"] > 0 and row["WILLR"] < -80)  # MACD動能轉正，WILLR超賣
        or (row["K"] < 20 and row["D"] < 20 and row["J"] < 0)  # KDJ三線超賣區
    )


def _is_sell_signal(row):
    """
    判斷是否符合賣出信號
    RSI > 70 OR MACD < 0 AND WILLR > -20 OR J > 100
    """
    return (
        (row["Close"] < row["MA"] and row["RSI"] > 70)  # 收盤價低於MA日均線且RSI超買
        or (row["MACD_Diff"] < 0 and row["WILLR"] > -20)  # MACD動能轉負，WILLR超買
        or (row["K"] > 80 and row["D"] > 80 and row["J"] > 100)  # KDJ三線超買區
    )
