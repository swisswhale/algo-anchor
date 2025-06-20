# core/utils/charting.py
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_strategy_chart(ticker, lookback, entry_threshold, exit_threshold):
    start_date = datetime.today() - timedelta(days=365)
    data = yf.download(ticker, start=start_date)
    data['Price'] = data['Adj Close']
    data['RollingMean'] = data['Price'].rolling(window=lookback).mean()
    data['RollingStd'] = data['Price'].rolling(window=lookback).std()
    data['ZScore'] = (data['Price'] - data['RollingMean']) / data['RollingStd']

    data['Signal'] = 0
    data.loc[data['ZScore'] > entry_threshold, 'Signal'] = -1
    data.loc[data['ZScore'] < -entry_threshold, 'Signal'] = 1
    data.loc[data['ZScore'].abs() < exit_threshold, 'Signal'] = 0

    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Price'], label='Price', color='blue')
    plt.plot(data.index, data['RollingMean'], label='Rolling Mean', color='orange')
    plt.scatter(data.index[data['Signal'] == 1], data['Price'][data['Signal'] == 1], color='green', label='Buy', marker='^')
    plt.scatter(data.index[data['Signal'] == -1], data['Price'][data['Signal'] == -1], color='red', label='Sell', marker='v')
    plt.title(f"{ticker} - Mean Reversion Strategy")
    plt.legend()
    plt.tight_layout()

    filename = f"strategy_{ticker}.png"
    path = f"core/static/img/{filename}"
    plt.savefig(path)
    plt.close()
    return f"/static/img/{filename}"