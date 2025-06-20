from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class Security(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=100, null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.symbol

class Strategy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="Descriptive name for your strategy")
    lookback_days = models.PositiveIntegerField(
        default=20, 
        help_text="Number of days for moving average calculation"
    )
    entry_threshold = models.FloatField(help_text="Z-score threshold for entry signal")
    exit_rule = models.CharField(
        max_length=255, 
        help_text="Exit strategy rule (e.g., mean_revert, stop_loss)"
    )
    tickers = models.ManyToManyField(Security, related_name='strategies', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Strategies"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def get_tickers_display(self):
        """Return comma-separated list of ticker symbols"""
        return ", ".join(ticker.symbol for ticker in self.tickers.all())
    
    def has_backtest_results(self):
        """Check if strategy has backtest results"""
        return hasattr(self, 'backtestresult') and self.backtestresult is not None
    
    def get_performance_summary(self):
        """Get a summary of performance metrics"""
        if self.has_backtest_results():
            result = self.backtestresult
            return {
                'return': result.cumulative_return,
                'sharpe': result.sharpe_ratio,
                'win_rate': result.win_rate,
                'max_drawdown': result.max_drawdown
            }
        return None

class PriceData(models.Model):
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
    date = models.DateField()
    close = models.FloatField()

    def __str__(self):
        return f"{self.security.symbol} - {self.date} - {self.close}"

class BacktestResult(models.Model):
    strategy = models.OneToOneField(Strategy, on_delete=models.CASCADE)
    cumulative_return = models.FloatField(null=True, blank=True)
    sharpe_ratio = models.FloatField(null=True, blank=True)
    win_rate = models.FloatField(null=True, blank=True)
    max_drawdown = models.FloatField(null=True, blank=True)
    trade_log = models.TextField(blank=True)

    def __str__(self):
        return f"Backtest for {self.strategy.name}"

@receiver(post_save, sender=Strategy)
def run_backtest_on_save(sender, instance, created, **kwargs):
    if created:
        # Pull data for each ticker
        tickers = instance.tickers.all()
        end = datetime.today()
        start = end - timedelta(days=instance.lookback_days * 5)

        price_data = {}

        for sec in tickers:
            try:
                df = yf.download(sec.symbol, start=start, end=end)
                df.reset_index(inplace=True)
                for _, row in df.iterrows():
                    PriceData.objects.get_or_create(
                        security=sec,
                        date=row['Date'].date(),
                        close=row['Close']
                    )
                price_data[sec.symbol] = df['Close']
            except Exception as e:
                print(f"Failed to fetch data for {sec.symbol}: {e}")

        # Simple backtest logic
        if len(price_data) == 1:
            series = list(price_data.values())[0]
            returns = series.pct_change().dropna()
            cumulative = (1 + returns).prod() - 1
            sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            drawdown = (series / series.cummax() - 1).min()
            wins = (returns > 0).sum()
            total = len(returns)
            win_rate = wins / total if total > 0 else 0

            BacktestResult.objects.create(
                strategy=instance,
                cumulative_return=cumulative,
                sharpe_ratio=sharpe,
                win_rate=win_rate,
                max_drawdown=drawdown,
                trade_log="Auto-generated on creation."
            )