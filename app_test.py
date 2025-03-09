import os
import pandas as pd

from app import main


if __name__ == "__main__":
    now = pd.Timestamp.now()

    ticker = "2330.TW"
    start_date = "2020-01-01"
    end_date = pd.Timestamp.today().strftime("%Y-%m-%d")
    query_data = False

    main(ticker, start_date, end_date, query_data)

    print("Spend time:", pd.Timestamp.now() - now)
