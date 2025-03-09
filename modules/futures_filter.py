import os
import pandas as pd
import streamlit as st
import ast

from utils.talib_utils import calculate_indicators
from utils.file_utils import read_folder_files


def load_existing_results(file_path):
    """加載已計算的技術指標結果"""
    if os.path.exists(file_path):
        result_data = pd.read_csv(file_path)
        with st.expander("已計算的技術指標結果"):
            st.dataframe(result_data, use_container_width=True)
        return {
            "ma": result_data["MA"].sort_values().unique().tolist(),
            "rsi": result_data["RSI"].sort_values().unique().tolist(),
            "macd": [
                ast.literal_eval(item)
                for item in result_data["MACD"].sort_values().unique().tolist()
            ],
            "willr": result_data["WILLR"].sort_values().unique().tolist(),
            "kdj": [
                ast.literal_eval(item)
                for item in result_data["KDJ"].sort_values().unique().tolist()
            ],
        }

    st.info("請先執行計算指標的功能，並選擇適合的參數組合。")
    return {"ma": [], "rsi": [], "macd": [], "willr": [], "kdj": []}


def get_user_inputs(defaults):
    """獲取用戶輸入的技術指標參數"""
    col1, col2 = st.columns(2)

    with col1:
        ma_periods = st.multiselect(
            "選擇移動平均線週期",
            [5, 10, 20, 60, 120],
            default=defaults["ma"] or [5, 10, 20],
        )
        rsi_periods = st.multiselect(
            "選擇相對強弱指數週期",
            [5, 10, 20, 60, 120],
            default=defaults["rsi"] or [5, 10, 20],
        )
        macd_params = st.multiselect(
            "選擇MACD參數",
            [(5, 34, 5), (12, 26, 9), (24, 52, 9), (48, 104, 9)],
            default=defaults["macd"] or [(12, 26, 9), (24, 52, 9), (48, 104, 9)],
        )
        willr_periods = st.multiselect(
            "選擇Williams %R週期",
            [5, 10, 20, 30, 60, 120],
            default=defaults["willr"] or [5, 10, 20],
        )
        kdj_params = st.multiselect(
            "選擇KDJ參數",
            [(9, 3, 3), (18, 3, 3), (36, 3, 3), (14, 3, 3)],
            default=defaults["kdj"] or [(9, 3, 3), (18, 3, 3), (36, 3, 3)],
        )

    with col2:
        ma_periods += parse_custom_input(
            st.text_input("輸入自訂的移動平均線週期（以逗號分隔）")
        )
        rsi_periods += parse_custom_input(
            st.text_input("輸入自訂的相對強弱指數週期（以逗號分隔）")
        )
        macd_params += parse_tuple_input(
            st.text_input("輸入自訂的MACD參數（格式為 fast,slow,signal）")
        )
        willr_periods += parse_custom_input(
            st.text_input("輸入自訂的Williams %R週期（以逗號分隔）")
        )
        kdj_params += parse_tuple_input(
            st.text_input("輸入自訂的KDJ參數（格式為 rsv, k, d）")
        )

    return (
        list(set(ma_periods)),
        list(set(rsi_periods)),
        list(set(macd_params)),
        list(set(willr_periods)),
        list(set(kdj_params)),
    )


def parse_custom_input(input_text):
    """解析用戶輸入的單一數值類型指標"""
    return (
        [int(x.strip()) for x in input_text.split(",") if x.strip().isdigit()]
        if input_text
        else []
    )


def parse_tuple_input(input_text):
    """解析用戶輸入的元組類型指標（MACD/KDJ）"""
    try:
        return [tuple(map(int, input_text.split(",")))] if input_text else []
    except ValueError:
        st.error("輸入格式錯誤，請使用正確的整數格式，例如 12,26,9")
        return []


def main():
    st.subheader("濾網交易訊號")
    ticker_list = sorted(set(read_folder_files("data")))
    if not ticker_list:
        st.stop()

    selected_ticker = st.selectbox("選擇股票代碼", ticker_list)
    result_file_path = os.path.join("data", f"{selected_ticker}_strategy_results.csv")
    default_params = load_existing_results(result_file_path)

    ma_periods, rsi_periods, macd_params, willr_periods, kdj_params = get_user_inputs(
        default_params
    )

    with st.expander("選擇結果"):
        st.write("選擇的移動平均線週期:", ma_periods)
        st.write("選擇的相對強弱指數週期:", rsi_periods)
        st.write("選擇的MACD參數:", macd_params)
        st.write("選擇的Williams %R週期:", willr_periods)
        st.write("選擇的KDJ參數:", kdj_params)
    save_condition = st.number_input("儲存獲利因子大於", 0, 10, 4, 1)

    if st.button("回測獲利因子", type="primary"):
        file_path = os.path.join("data", f"{selected_ticker}_raw_data.csv")
        try:
            data = pd.read_csv(file_path)
            with st.spinner("正在計算獲利因子..."):
                calculate_indicators(
                    selected_ticker,
                    data,
                    ma_periods,
                    rsi_periods,
                    macd_params,
                    willr_periods,
                    kdj_params,
                    save_condition,
                )
            st.success("計算完成！")
        except Exception as e:
            st.error(f"處理數據時發生錯誤: {e}")


main()
