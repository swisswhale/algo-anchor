"""
Advanced Backtesting Engine for AlgoAnchor
Provides comprehensive backtesting capabilities with detailed performance metrics.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Advanced backtesting engine that supports multiple strategies and provides
    comprehensive performance metrics and trade logging.
    """
    
    def __init__(self, strategy, commission_rate=0.001):
        self.strategy = strategy
        self.commission_rate = commission_rate
        self.data = {}
        self.results = {}
        self.trade_log = []
        
    def fetch_data(self, start_date: datetime, end_date: datetime) -> bool:
        """Fetch historical data for all strategy tickers"""
        try:
            tickers = self.strategy.tickers.all()
            self.data = {}
            
            for security in tickers:
                try:
                    ticker_data = yf.download(
                        security.symbol, 
                        start=start_date, 
                        end=end_date,
                        progress=False,
                        auto_adjust=True
                    )
                    
                    if ticker_data.empty:
                        logger.warning(f"No data found for {security.symbol}")
                        continue
                    
                    # Handle MultiIndex columns (yfinance returns this for single tickers too)
                    if hasattr(ticker_data.columns, 'levels'):
                        # MultiIndex columns - flatten them
                        ticker_data.columns = ticker_data.columns.droplevel(1)
                    
                    # Clean and prepare data
                    ticker_data = ticker_data.dropna()
                    
                    # Ensure we have the right column names
                    if 'Close' not in ticker_data.columns:
                        logger.error(f"No 'Close' column found for {security.symbol}")
                        logger.debug(f"Available columns: {ticker_data.columns.tolist()}")
                        continue
                    
                    ticker_data['Returns'] = ticker_data['Close'].pct_change()
                    ticker_data['Security'] = security
                    
                    self.data[security.symbol] = ticker_data
                    logger.info(f"Successfully loaded {len(ticker_data)} data points for {security.symbol}")
                    
                except Exception as e:
                    logger.error(f"Error fetching data for {security.symbol}: {str(e)}")
                    continue
                
            return len(self.data) > 0
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            return False
    
    def run_mean_reversion_strategy(self) -> Dict:
        """Execute mean reversion strategy backtest"""
        if not self.data:
            return {}
            
        all_trades = []
        portfolio_value = []
        benchmark_returns = []
        
        # Get strategy parameters
        lookback = self.strategy.lookback_days
        entry_threshold = self.strategy.entry_threshold
        # Use a default exit threshold since it's not in the model
        exit_threshold = entry_threshold * 0.5  # Exit at half the entry threshold
        
        for symbol, data in self.data.items():
            if len(data) < lookback + 1:
                continue
                
            # Calculate mean reversion signals
            data = self._calculate_mean_reversion_signals(
                data, lookback, entry_threshold, exit_threshold
            )
            
            # Execute trades
            trades = self._execute_trades(data, symbol)
            all_trades.extend(trades)
            
            # Track portfolio performance
            data['Strategy_Returns'] = data['Returns'] * data['Position'].shift(1)
            portfolio_value.extend(data['Strategy_Returns'].fillna(0).tolist())
            benchmark_returns.extend(data['Returns'].fillna(0).tolist())
        
        # Calculate comprehensive metrics
        return self._calculate_performance_metrics(
            portfolio_value, benchmark_returns, all_trades
        )
    
    def _calculate_mean_reversion_signals(self, data: pd.DataFrame, lookback: int, 
                                        entry_threshold: float, exit_threshold: float) -> pd.DataFrame:
        """Calculate mean reversion trading signals"""
        # Rolling statistics
        data['Rolling_Mean'] = data['Close'].rolling(window=lookback).mean()
        data['Rolling_Std'] = data['Close'].rolling(window=lookback).std()
        data['Z_Score'] = (data['Close'] - data['Rolling_Mean']) / data['Rolling_Std']
        
        # Generate signals
        data['Signal'] = 0
        data.loc[data['Z_Score'] < -entry_threshold, 'Signal'] = 1  # Buy signal
        data.loc[data['Z_Score'] > entry_threshold, 'Signal'] = -1  # Sell signal
        data.loc[data['Z_Score'].abs() < exit_threshold, 'Signal'] = 0  # Exit signal
        
        # Generate positions
        data['Position'] = 0
        position = 0
        
        for i in range(len(data)):
            if data.iloc[i]['Signal'] == 1 and position == 0:
                position = 1
            elif data.iloc[i]['Signal'] == -1 and position == 0:
                position = -1
            elif data.iloc[i]['Signal'] == 0:
                position = 0
            
            data.iloc[i, data.columns.get_loc('Position')] = position
        
        return data
    
    def _execute_trades(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """Execute trades based on position changes"""
        trades = []
        position_changes = data[data['Position'].diff() != 0].copy()
        
        for idx, row in position_changes.iterrows():
            if pd.isna(row['Position']) or row['Position'] == 0:
                continue
                
            trade_type = 'BUY' if row['Position'] > 0 else 'SELL'
            price = row['Close']
            commission = price * self.commission_rate
            
            trade = {
                'symbol': symbol,
                'date': idx.date() if hasattr(idx, 'date') else idx,
                'type': trade_type,
                'price': price,
                'quantity': 100,  # Standard lot size
                'commission': commission,
                'signal_value': row['Z_Score'],
                'security': row['Security']
            }
            
            trades.append(trade)
        
        return trades
    
    def _calculate_performance_metrics(self, portfolio_returns: List[float], 
                                     benchmark_returns: List[float], 
                                     trades: List[Dict]) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not portfolio_returns:
            return {}
            
        portfolio_returns = np.array(portfolio_returns)
        benchmark_returns = np.array(benchmark_returns)
        
        # Basic returns
        cumulative_return = np.prod(1 + portfolio_returns) - 1
        annualized_return = (1 + cumulative_return) ** (252 / len(portfolio_returns)) - 1
        
        # Risk metrics
        volatility = np.std(portfolio_returns) * np.sqrt(252)
        sharpe_ratio = (np.mean(portfolio_returns) * 252) / volatility if volatility > 0 else 0
        
        # Downside deviation and Sortino ratio
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_deviation = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = (np.mean(portfolio_returns) * 252) / downside_deviation if downside_deviation > 0 else 0
        
        # Drawdown analysis
        cumulative_returns = np.cumprod(1 + portfolio_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown)
        
        # Trade analysis
        trade_returns = []
        if trades:
            for i in range(0, len(trades) - 1, 2):  # Assuming pairs of entry/exit
                if i + 1 < len(trades):
                    entry_price = trades[i]['price']
                    exit_price = trades[i + 1]['price']
                    trade_return = (exit_price - entry_price) / entry_price
                    trade_returns.append(trade_return)
        
        winning_trades = len([r for r in trade_returns if r > 0])
        losing_trades = len([r for r in trade_returns if r <= 0])
        win_rate = winning_trades / len(trade_returns) if trade_returns else 0
        
        avg_winning_trade = np.mean([r for r in trade_returns if r > 0]) if winning_trades > 0 else 0
        avg_losing_trade = np.mean([r for r in trade_returns if r <= 0]) if losing_trades > 0 else 0
        avg_trade_return = np.mean(trade_returns) if trade_returns else 0
        
        # Risk metrics
        var_95 = np.percentile(portfolio_returns, 5) if len(portfolio_returns) > 0 else 0
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Benchmark comparison
        benchmark_cumulative = np.prod(1 + benchmark_returns) - 1
        alpha = cumulative_return - benchmark_cumulative
        
        # Beta calculation (correlation with benchmark)
        if len(portfolio_returns) > 1 and len(benchmark_returns) > 1:
            covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1
        else:
            beta = 1
        
        return {
            'cumulative_return': cumulative_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'total_trades': len(trades),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'avg_trade_return': avg_trade_return,
            'avg_winning_trade': avg_winning_trade,
            'avg_losing_trade': avg_losing_trade,
            'value_at_risk_95': var_95,
            'calmar_ratio': calmar_ratio,
            'benchmark_return': benchmark_cumulative,
            'alpha': alpha,
            'beta': beta,
            'trade_log': trades
        }
    
    def run_momentum_strategy(self) -> Dict:
        """Execute momentum strategy backtest"""
        # Placeholder for momentum strategy
        # Can be implemented based on specific momentum rules
        return {}
    
    def run_pairs_trading_strategy(self) -> Dict:
        """Execute pairs trading strategy backtest"""
        # Placeholder for pairs trading strategy
        # Can be implemented for multi-ticker strategies
        return {}


def run_comprehensive_backtest(strategy) -> Dict:
    """
    Main function to run comprehensive backtest for a strategy
    """
    engine = BacktestEngine(strategy)
    
    # Calculate backtest period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=strategy.lookback_days * 10)  # Extended period for analysis
    
    # Fetch data
    if not engine.fetch_data(start_date, end_date):
        logger.error(f"Failed to fetch data for strategy {strategy.name}")
        return {}
    
    # Run mean reversion strategy (default for current model)
    results = engine.run_mean_reversion_strategy()
    
    # Add metadata
    results['backtest_start_date'] = start_date.date()
    results['backtest_end_date'] = end_date.date()
    
    return results
