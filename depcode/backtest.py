import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def run_mean_reversion_backtest(ticker, lookback, entry_threshold, exit_threshold):
    start_date = datetime.today() - timedelta(days=365)
    data = yf.download(ticker, start=start_date)
    data['Price'] = data['Adj Close']

    # Calculate rolling stats
    data['RollingMean'] = data['Price'].rolling(window=lookback).mean()
    data['RollingStd'] = data['Price'].rolling(window=lookback).std()
    data['ZScore'] = (data['Price'] - data['RollingMean']) / data['RollingStd']

    # Signal logic
    data['Position'] = 0
    data.loc[data['ZScore'] < -entry_threshold, 'Position'] = 1
    data.loc[data['ZScore'] > entry_threshold, 'Position'] = -1
    data.loc[data['ZScore'].abs() < exit_threshold, 'Position'] = 0

    data['Position'] = data['Position'].replace(to_replace=0, method='ffill').shift()
    data['Returns'] = data['Price'].pct_change()
    data['Strategy'] = data['Returns'] * data['Position']

    # Performance
    data['CumulativeMarket'] = (1 + data['Returns']).cumprod()
    data['CumulativeStrategy'] = (1 + data['Strategy']).cumprod()

    # Metrics
    cumulative_return = data['CumulativeStrategy'].iloc[-1] - 1
    sharpe_ratio = np.sqrt(252) * data['Strategy'].mean() / data['Strategy'].std()

    # Trade analysis
    trades = data[data['Position'].diff() != 0][['Position']]
    trades['Action'] = trades['Position'].apply(lambda x: 'Buy' if x == 1 else 'Sell' if x == -1 else 'Exit')
    trades['Returns'] = data['Returns'].loc[trades.index].fillna(0)
    trades['Profit'] = trades['Returns'] > 0
    win_rate = trades['Profit'].mean()

    # Drawdown
    data['Peak'] = data['CumulativeStrategy'].cummax()
    data['Drawdown'] = (data['CumulativeStrategy'] - data['Peak']) / data['Peak']
    max_drawdown = data['Drawdown'].min()

    return {
        "cumulative_return": round(cumulative_return, 4),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "win_rate": f"{round(win_rate * 100, 2)}%",
        "max_drawdown": f"{round(max_drawdown * 100, 2)}%",
        "trade_count": len(trades),
        "backtest_df": data,
        "trade_log": trades
    }