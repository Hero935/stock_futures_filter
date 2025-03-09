import os
import streamlit as st
import pandas as pd

from utils.file_utils import read_folder_files
from utils.plotly_utils import plot_chart


def main():
    st.subheader("資料分析圖表")

    ticker_list = sorted(set(read_folder_files("data")))
    ticker = st.selectbox("請選擇股票", ticker_list)

    file_path = os.path.join("data", f"{ticker}_strategy_results.csv")
    data = pd.read_csv(file_path)
    df = pd.DataFrame(data)
    selected_row = st.dataframe(
        df,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True,
    )
    print(selected_row.selection)
    if selected_row.selection["rows"]:
        index = selected_row.selection["rows"][0]
        ma_period = df["MA"].iloc[index]
        rsi_period = df["RSI"].iloc[index]
        macd = df["MACD"].iloc[index]
        willr_period = df["WILLR"].iloc[index]
        kdj = df["KDJ"].iloc[index]

        file_name = f"{ticker}_MA({ma_period})_RSI({rsi_period})_MACD{macd}_WILLR({willr_period})_KDJ{kdj}.csv"
        file_path = os.path.join("data_results", file_name)
        print(file_path)
        if os.path.exists(file_path):
            df_result = pd.read_csv(file_path)
            with st.expander("策略分析結果"):
                st.dataframe(df_result, use_container_width=True)
            _ = plot_chart(df_result)

        else:
            st.write("資料尚未產生")


main()
