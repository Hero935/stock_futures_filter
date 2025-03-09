import streamlit as st
import yaml
import os
import pandas as pd
from datetime import date, timedelta

from utils.file_utils import read_folder_files
from utils.signal_utils import SignalEvaluator


def parse_conditions(conditions):
    """將 YAML 條件轉換為可讀的條件語句"""
    if isinstance(conditions, list):
        return " or ".join([f"({c})" for c in conditions])
    return str(conditions)


def main():
    st.subheader("📊 股票買賣信號設定")

    evaluator = SignalEvaluator()
    config = evaluator.load_yaml_config()

    col1, col2 = st.columns(2)

    with col1:
        st.write("🟢 買入信號設定")
        buy_yaml_text = st.text_area(
            "請編輯買入信號 YAML",
            value=yaml.dump({"buy_signal": config["buy_signal"]}, allow_unicode=True),
            height=300,
            key="buy_yaml",
        )

    with col2:
        st.write("🔴 賣出信號設定")
        sell_yaml_text = st.text_area(
            "請編輯賣出信號 YAML",
            value=yaml.dump({"sell_signal": config["sell_signal"]}, allow_unicode=True),
            height=300,
            key="sell_yaml",
        )

    is_valid_yaml = True
    parsed_buy_yaml, parsed_sell_yaml = None, None

    try:
        parsed_buy_yaml = yaml.safe_load(buy_yaml_text)
        parsed_sell_yaml = yaml.safe_load(sell_yaml_text)
    except yaml.YAMLError as e:
        is_valid_yaml = False
        st.error(f"YAML 格式錯誤：\n{e}")

    if is_valid_yaml and parsed_buy_yaml and parsed_sell_yaml:
        col1.code(
            f"買入條件:\n{parse_conditions(parsed_buy_yaml.get('buy_signal', '無'))}",
            wrap_lines=True,
        )
        col2.code(
            f"賣出條件:\n{parse_conditions(parsed_sell_yaml.get('sell_signal', '無'))}",
            wrap_lines=True,
        )

    if st.button("💾 儲存設定"):
        if is_valid_yaml:
            config.update(parsed_buy_yaml)
            config.update(parsed_sell_yaml)
            evaluator.save_yaml_config(config)
            st.success("設定已成功儲存！")
        else:
            st.error("❌ 無法儲存，請修正 YAML 格式錯誤！")

    st.subheader("📈 測試市場數據")
    c1, c2, c3 = st.columns(3)
    ticker_list = sorted(set(read_folder_files("data")))
    ticker = c1.selectbox("請選擇股票代號", ticker_list)
    start_date = pd.to_datetime(
        c2.date_input("請選擇開始日期", date.today() - timedelta(days=365))
    )
    end_date = pd.to_datetime(c3.date_input("請選擇結束日期", date.today()))

    file_path = os.path.join("data", f"{ticker}_raw_data.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
        with st.expander(f"{ticker} 近期交易紀錄"):
            st.dataframe(df, use_container_width=True)


main()
