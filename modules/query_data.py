import os
import pandas as pd
import streamlit as st
from datetime import datetime
from utils.yfinance_utils import get_data
from utils.file_utils import read_folder_files


def main():
    st.subheader("歷史資料更新")
    ticker_list = sorted(set(read_folder_files("data")))

    ticker_choice = st.selectbox("請選擇股票代號", ["新增股票代號"] + ticker_list)
    ticker = (
        st.text_input("請輸入股票代號", "2330.TW")
        if ticker_choice == "新增股票代號"
        else ticker_choice
    )

    file_path = os.path.join("data", f"{ticker}_raw_data.csv")
    latest_date = pd.Timestamp("2020-01-01")

    if os.path.exists(file_path):
        data = pd.read_csv(file_path, parse_dates=["Date"])
        with st.expander("檢視歷史資料"):
            st.dataframe(
                data.sort_values("Date", ascending=False), use_container_width=True
            )
        latest_date = data["Date"].max()

    start_date = st.date_input("起始日期", latest_date)
    end_date = st.date_input("結束日期", pd.Timestamp.now())

    col1, col2, col3 = st.columns(3)

    if col1.button("下載歷史資料", type="primary"):
        try:
            with st.spinner("下載中..."):
                data = get_data(ticker, start_date, end_date)
                if not data.empty:
                    data.to_csv(file_path, index=False)
                    st.success("資料下載完成！")
                else:
                    st.warning("未獲取到新數據，請檢查股票代號或日期範圍！")
        except Exception as e:
            st.error(f"下載失敗: {e}")

    if col2.button("刪除歷史資料", type="primary"):
        if os.path.exists(file_path):
            os.remove(file_path)
            st.success("歷史資料已刪除！")
        else:
            st.warning("文件不存在，無需刪除！")

    if col3.button("更新所有資料", type="secondary"):
        for ticker in ticker_list:
            file_path = os.path.join("data", f"{ticker}_raw_data.csv")
            if os.path.exists(file_path):
                existing_data = pd.read_csv(file_path, parse_dates=["Date"])
                latest_date = existing_data["Date"].max()
                try:
                    new_data = get_data(ticker, latest_date, end_date)
                    if not new_data.empty:
                        updated_data = (
                            pd.concat([existing_data, new_data])
                            .drop_duplicates(subset="Date")
                            .sort_values("Date", ascending=False)
                        )
                        updated_data.to_csv(file_path, index=False)
                        st.success(f"{ticker} 資料更新完成！")
                    else:
                        st.info(f"{ticker} 無新數據。")
                except Exception as e:
                    st.error(f"更新 {ticker} 失敗: {e}")
            else:
                st.warning(f"{ticker} 的資料文件不存在，無法更新！")


main()
