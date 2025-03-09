import yfinance as yf


def get_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date).reset_index()
    data.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    return data
