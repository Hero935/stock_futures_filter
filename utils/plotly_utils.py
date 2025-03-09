import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def plot_chart(df_result):
    # 讀取資料（假設 df_result 已存在）
    df = df_result.copy()

    # 確保 Date 欄位為 datetime 格式
    df["Date"] = pd.to_datetime(df["Date"])

    # 建立 Plotly 圖表
    fig = go.Figure()

    # 繪製收盤價線圖
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Close"],
            mode="lines",
            name="Close Price",
            line=dict(color="blue"),
        )
    )

    # 標註買賣點（Signal: 1 -> 買入，-1 -> 賣出）
    buy_signals = df[df["Signal"] == 1]
    sell_signals = df[df["Signal"] == -1]

    fig.add_trace(
        go.Scatter(
            x=buy_signals["Date"],
            y=buy_signals["Close"],
            mode="markers",
            marker=dict(color="green", size=10, symbol="triangle-up"),
            name="Buy Signal",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=sell_signals["Date"],
            y=sell_signals["Close"],
            mode="markers",
            marker=dict(color="red", size=10, symbol="triangle-down"),
            name="Sell Signal",
        )
    )

    # 設定圖表標題與格式
    fig.update_layout(
        title="Stock Price with Buy/Sell Signals",
        xaxis_title="Date",
        yaxis_title="Close Price",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        hovermode="x unified",
    )

    # 顯示主圖表
    st.plotly_chart(fig)

    # 額外附加 Volume 圖表
    fig_volume = go.Figure()
    fig_volume.add_trace(
        go.Bar(x=df["Date"], y=df["Volume"], name="Volume", marker_color="gray")
    )
    fig_volume.update_layout(
        title="Trading Volume", xaxis_title="Date", yaxis_title="Volume"
    )
    st.plotly_chart(fig_volume)

    # 額外附加 MACD_Diff 圖表
    if "MACD_Diff" in df.columns:
        fig_macd = go.Figure()
        fig_macd.add_trace(
            go.Bar(x=df["Date"], y=df["MACD_Diff"], name="MACD_Diff", marker_color="purple")
        )
        fig_macd.update_layout(
            title="MACD Difference", xaxis_title="Date", yaxis_title="MACD Diff"
        )
        st.plotly_chart(fig_macd)

    # 額外附加 RSI 圖表
    if "RSI" in df.columns:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(
            go.Scatter(
                x=df["Date"], y=df["RSI"], mode="lines", name="RSI", line=dict(color="orange")
            )
        )
        fig_rsi.update_layout(
            title="Relative Strength Index (RSI)",
            xaxis_title="Date",
            yaxis_title="RSI",
            yaxis=dict(range=[0, 100]),
        )
        st.plotly_chart(fig_rsi)
