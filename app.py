import streamlit as st


def main():

    st.set_page_config(
        page_title="Smart Stock",
        page_icon=":material/filter:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    query_data = st.Page(
        "modules/query_data.py", title="歷史資料更新", icon=":material/download:"
    )
    set_signal = st.Page(
        "modules/signal_definition.py", title="買賣信號條件", icon=":material/edit:"
    )
    futures_filter = st.Page(
        "modules/futures_Filter.py", title="濾網交易訊號", icon=":material/filter:"
    )
    plot_data = st.Page(
        "modules/data_analysis.py", title="資料分析圖表", icon=":material/analytics:"
    )

    pg = st.navigation([query_data, set_signal, futures_filter, plot_data])
    pg.run()


if __name__ == "__main__":
    main()
