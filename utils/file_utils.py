import os
import streamlit as st

def read_folder_files(folder_path):
    """讀取指定資料夾內的股票數據文件名稱"""
    try:
        files_list = os.listdir(folder_path)
    except FileNotFoundError:
        st.error("數據文件夾未找到，請檢查路徑是否正確。")
        return []
    except Exception as e:
        st.error(f"讀取文件夾時發生錯誤: {e}")
        return []

    key_name = "_raw_data"
    return [
        file.split(key_name)[0]
        for file in files_list
        if file.endswith(f"{key_name}.csv")
    ]
