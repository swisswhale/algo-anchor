"""
Advanced charting utilities for AlgoAnchor
Provides interactive charts with Plotly for strategy visualization
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from core.models import Strategy, BacktestResult, TradeLog
import logging

logger = logging.getLogger(__name__)


class StrategyChartGenerator:
    """Generate comprehensive strategy analysis charts"""
    
    def __init__(self, strategy):
        self.strategy = strategy
        self.data = None
        
    def fetch_chart_data(self, days=252):
        """Fetch data for charting (1 year default)"""
        try:
            tickers = self.strategy.tickers.all()
            if not tickers:
                return None
                
            # For now, focus on single ticker strategies
            ticker = tickers[0]
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch data
            data = yf.download(
                ticker.symbol,
                start=start_date,
                end=end_date,
                progress=False,
                auto_adjust=True
            )
            
            if data.empty:
                return None
                
            # Handle MultiIndex columns
            if hasattr(data.columns, 'levels'):
                data.columns = data.columns.droplevel(1)
                
            # Calculate technical indicators
            data = self._calculate_technical_indicators(data)
            
            self.data = data
            return data
            
        except Exception as e:
            logger.error(f"Error fetching chart data: {str(e)}")
            return None
    
    def _calculate_technical_indicators(self, data):
        """Calculate technical indicators for the strategy"""
        lookback = self.strategy.lookback_days
        entry_threshold = self.strategy.entry_threshold
        exit_threshold = entry_threshold * 0.5  # Default exit threshold
        
        # Rolling statistics
        data['SMA'] = data['Close'].rolling(window=lookback).mean()
        data['STD'] = data['Close'].rolling(window=lookback).std()
        data['Upper_Band'] = data['SMA'] + (2 * data['STD'])
        data['Lower_Band'] = data['SMA'] - (2 * data['STD'])
        
        # Z-Score calculation
        data['Z_Score'] = (data['Close'] - data['SMA']) / data['STD']
        
        # Entry/Exit signals
        data['Buy_Signal'] = data['Z_Score'] < -entry_threshold
        data['Sell_Signal'] = data['Z_Score'] > entry_threshold
        data['Exit_Signal'] = data['Z_Score'].abs() < exit_threshold
        
        # Mark signal points
        data['Buy_Points'] = data['Close'].where(data['Buy_Signal'])
        data['Sell_Points'] = data['Close'].where(data['Sell_Signal'])
        data['Exit_Points'] = data['Close'].where(data['Exit_Signal'])
        
        return data
    
    def generate_price_chart(self):
        """Generate main price chart with signals"""
        if self.data is None:
            return None
            
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=(
                f"{self.strategy.tickers.first().symbol} Price with Strategy Signals",
                "Z-Score", 
                "Volume"
            ),
            row_heights=[0.6, 0.25, 0.15]
        )
        
        # Main price chart
        fig.add_trace(
            go.Candlestick(
                x=self.data.index,
                open=self.data['Open'],
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'],
                name="Price",
                increasing_line_color='#00ff88',
                decreasing_line_color='#ff4444'
            ),
            row=1, col=1
        )
        
        # Simple Moving Average
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['SMA'],
                mode='lines',
                name=f'SMA ({self.strategy.lookback_days})',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # Bollinger Bands
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['Upper_Band'],
                mode='lines',
                name='Upper Band',
                line=dict(color='gray', width=1, dash='dash'),
                showlegend=False
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['Lower_Band'],
                mode='lines',
                name='Lower Band',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)'
            ),
            row=1, col=1
        )
        
        # Buy signals
        buy_points = self.data.dropna(subset=['Buy_Points'])
        if not buy_points.empty:
            fig.add_trace(
                go.Scatter(
                    x=buy_points.index,
                    y=buy_points['Buy_Points'],
                    mode='markers',
                    name='Buy Signal',
                    marker=dict(
                        symbol='triangle-up',
                        size=12,
                        color='green'
                    )
                ),
                row=1, col=1
            )
        
        # Sell signals
        sell_points = self.data.dropna(subset=['Sell_Points'])
        if not sell_points.empty:
            fig.add_trace(
                go.Scatter(
                    x=sell_points.index,
                    y=sell_points['Sell_Points'],
                    mode='markers',
                    name='Sell Signal',
                    marker=dict(
                        symbol='triangle-down',
                        size=12,
                        color='red'
                    )
                ),
                row=1, col=1
            )
        
        # Z-Score subplot
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data['Z_Score'],
                mode='lines',
                name='Z-Score',
                line=dict(color='purple', width=2)
            ),
            row=2, col=1
        )
        
        # Z-Score thresholds
        fig.add_hline(
            y=self.strategy.entry_threshold,
            line_dash="dash",
            line_color="red",
            annotation_text="Sell Threshold",
            row=2, col=1
        )
        
        fig.add_hline(
            y=-self.strategy.entry_threshold,
            line_dash="dash",
            line_color="green",
            annotation_text="Buy Threshold",
            row=2, col=1
        )
        
        fig.add_hline(
            y=0,
            line_dash="solid",
            line_color="black",
            line_width=1,
            row=2, col=1
        )
        
        # Volume subplot
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(self.data['Close'], self.data['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=self.data.index,
                y=self.data['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f"{self.strategy.name} - Strategy Analysis",
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True,
            hovermode='x unified'
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Z-Score", row=2, col=1)
        fig.update_yaxes(title_text="Volume", row=3, col=1)
        
        return fig
    
    def generate_performance_chart(self):
        """Generate performance comparison chart"""
        try:
            backtest_result = self.strategy.backtestresult
        except:
            return None
            
        if not backtest_result or self.data is None:
            return None
            
        # Calculate strategy returns vs benchmark
        returns = self.data['Close'].pct_change().fillna(0)
        
        # Simple buy-and-hold benchmark
        benchmark_cumulative = (1 + returns).cumprod()
        
        # For strategy performance, we'd need to implement the actual strategy
        # For now, create a mock strategy performance
        strategy_returns = returns.copy()
        
        # Apply basic mean reversion logic
        z_scores = self.data['Z_Score'].fillna(0)
        position = np.where(z_scores < -self.strategy.entry_threshold, 1,
                           np.where(z_scores > self.strategy.entry_threshold, -1, 0))
        
        # Forward fill positions
        position = pd.Series(position, index=self.data.index)
        position = position.replace(0, np.nan).ffill().fillna(0)
        
        strategy_returns = returns * position.shift(1)
        strategy_cumulative = (1 + strategy_returns.fillna(0)).cumprod()
        
        fig = go.Figure()
        
        # Benchmark performance
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=benchmark_cumulative,
                mode='lines',
                name='Buy & Hold',
                line=dict(color='blue', width=2)
            )
        )
        
        # Strategy performance
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=strategy_cumulative,
                mode='lines',
                name='Strategy',
                line=dict(color='green', width=2)
            )
        )
        
        fig.update_layout(
            title="Strategy Performance vs Buy & Hold",
            xaxis_title="Date",
            yaxis_title="Cumulative Returns",
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def generate_stats_summary(self):
        """Generate summary statistics"""
        if self.data is None:
            return {}
            
        try:
            backtest = getattr(self.strategy, 'backtestresult', None)
            
            stats = {
                'data_points': len(self.data),
                'avg_z_score': self.data['Z_Score'].mean(),
                'z_score_std': self.data['Z_Score'].std(),
                'current_z_score': self.data['Z_Score'].iloc[-1] if len(self.data) > 0 else 0,
                'price_volatility': self.data['Close'].pct_change().std() * np.sqrt(252),
                'current_price': self.data['Close'].iloc[-1] if len(self.data) > 0 else 0,
                'avg_volume': self.data['Volume'].mean(),
                'backtest_return': backtest.cumulative_return if backtest else None,
                'backtest_sharpe': backtest.sharpe_ratio if backtest else None,
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating stats: {str(e)}")
            return {}


def generate_strategy_chart_html(strategy):
    """Generate HTML for strategy charts"""
    try:
        generator = StrategyChartGenerator(strategy)
        
        data = generator.fetch_chart_data()
        if data is None or data.empty:
            return None, None, {}
            
        # Generate charts
        price_chart = generator.generate_price_chart()
        performance_chart = generator.generate_performance_chart()
        stats = generator.generate_stats_summary()
        
        # Convert to HTML
        price_chart_html = price_chart.to_html(
            include_plotlyjs='cdn',
            div_id="price-chart"
        ) if price_chart else None
        
        performance_chart_html = performance_chart.to_html(
            include_plotlyjs=False,
            div_id="performance-chart"
        ) if performance_chart else None
        
        return price_chart_html, performance_chart_html, stats
        
    except Exception as e:
        logger.error(f"Error generating strategy charts: {str(e)}")
        return None, None, {}


def generate_trade_markers_data(strategy):
    """Generate trade markers for chart overlay"""
    try:
        backtest_result = getattr(strategy, 'backtestresult', None)
        if not backtest_result:
            return []
            
        trades = TradeLog.objects.filter(backtest_result=backtest_result).order_by('date')
        
        markers = []
        for trade in trades:
            markers.append({
                'date': trade.date.isoformat(),
                'price': trade.price,
                'type': trade.trade_type,
                'symbol': trade.security.symbol,
                'signal': trade.signal_value,
                'color': 'green' if trade.trade_type == 'BUY' else 'red'
            })
            
        return markers
        
    except Exception as e:
        logger.error(f"Error generating trade markers: {str(e)}")
        return []


# Legacy function for backward compatibility
def generate_strategy_chart(ticker, lookback, entry_threshold, exit_threshold):
    """Legacy matplotlib chart function - kept for compatibility"""
    return None