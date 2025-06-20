from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Security(models.Model):
    EXCHANGE_CHOICES = [
        ('NYSE', 'New York Stock Exchange'),
        ('NASDAQ', 'NASDAQ'),
        ('AMEX', 'American Stock Exchange'),
        ('OTHER', 'Other'),
    ]
    
    MARKET_CAP_CHOICES = [
        ('LARGE', 'Large Cap (>$10B)'),
        ('MID', 'Mid Cap ($2B-$10B)'),
        ('SMALL', 'Small Cap (<$2B)'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    symbol = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=200, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    market_cap_category = models.CharField(
        max_length=10, 
        choices=MARKET_CAP_CHOICES, 
        default='UNKNOWN'
    )
    exchange = models.CharField(
        max_length=10, 
        choices=EXCHANGE_CHOICES, 
        default='OTHER',
        blank=True
    )
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Securities"
        ordering = ['symbol']

    def __str__(self):
        return f"{self.symbol} - {self.name}" if self.name else self.symbol
    
    def get_market_cap_display_value(self):
        """Return formatted market cap"""
        if self.market_cap:
            if self.market_cap >= 1e12:
                return f"${self.market_cap/1e12:.1f}T"
            elif self.market_cap >= 1e9:
                return f"${self.market_cap/1e9:.1f}B"
            elif self.market_cap >= 1e6:
                return f"${self.market_cap/1e6:.1f}M"
            else:
                return f"${self.market_cap:,.0f}"
        return "N/A"
    
    def update_market_cap_category(self):
        """Update market cap category based on market cap value"""
        if self.market_cap:
            if self.market_cap >= 10e9:  # $10B+
                self.market_cap_category = 'LARGE'
            elif self.market_cap >= 2e9:  # $2B-$10B
                self.market_cap_category = 'MID'
            else:  # <$2B
                self.market_cap_category = 'SMALL'
        else:
            self.market_cap_category = 'UNKNOWN'
    
    def save(self, *args, **kwargs):
        self.update_market_cap_category()
        super().save(*args, **kwargs)

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
    # Performance metrics
    cumulative_return = models.FloatField(null=True, blank=True)
    annualized_return = models.FloatField(null=True, blank=True)
    sharpe_ratio = models.FloatField(null=True, blank=True)
    sortino_ratio = models.FloatField(null=True, blank=True)
    win_rate = models.FloatField(null=True, blank=True)
    max_drawdown = models.FloatField(null=True, blank=True)
    volatility = models.FloatField(null=True, blank=True)
    # Trade statistics
    total_trades = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    avg_trade_return = models.FloatField(null=True, blank=True)
    avg_winning_trade = models.FloatField(null=True, blank=True)
    avg_losing_trade = models.FloatField(null=True, blank=True)
    # Risk metrics
    value_at_risk_95 = models.FloatField(null=True, blank=True)
    calmar_ratio = models.FloatField(null=True, blank=True)
    # Benchmark comparison
    benchmark_return = models.FloatField(null=True, blank=True)
    alpha = models.FloatField(null=True, blank=True)
    beta = models.FloatField(null=True, blank=True)
    # Execution details
    backtest_start_date = models.DateField(null=True, blank=True)
    backtest_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Backtest for {self.strategy.name}"
    
    def get_performance_summary(self):
        """Return formatted performance summary"""
        return {
            'return': f"{self.cumulative_return:.2%}" if self.cumulative_return else "N/A",
            'sharpe': f"{self.sharpe_ratio:.2f}" if self.sharpe_ratio else "N/A",
            'win_rate': f"{self.win_rate:.1%}" if self.win_rate else "N/A",
            'max_drawdown': f"{self.max_drawdown:.2%}" if self.max_drawdown else "N/A",
            'total_trades': self.total_trades,
        }

class TradeLog(models.Model):
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('EXIT', 'Exit'),
    ]
    
    backtest_result = models.ForeignKey(BacktestResult, on_delete=models.CASCADE, related_name='trades')
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    date = models.DateField()
    price = models.FloatField()
    quantity = models.IntegerField(default=1)
    commission = models.FloatField(default=0.0)
    pnl = models.FloatField(null=True, blank=True)  # Profit/Loss for this trade
    cumulative_pnl = models.FloatField(null=True, blank=True)
    signal_value = models.FloatField(null=True, blank=True)  # Z-score or signal strength
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'id']

    def __str__(self):
        return f"{self.trade_type} {self.security.symbol} on {self.date}"

@receiver(post_save, sender=Strategy)
def run_backtest_on_save(sender, instance, created, **kwargs):
    """Auto-trigger comprehensive backtesting when a strategy is created"""
    if created and hasattr(instance, 'user') and instance.user:
        from .services.backtest_engine import run_comprehensive_backtest
        try:
            # Run comprehensive backtest
            results = run_comprehensive_backtest(instance)
            
            if not results:
                logger.warning(f"No backtest results generated for strategy {instance.name}")
                return
            
            # Create BacktestResult
            backtest_result = BacktestResult.objects.create(
                strategy=instance,
                cumulative_return=results.get('cumulative_return'),
                annualized_return=results.get('annualized_return'),
                sharpe_ratio=results.get('sharpe_ratio'),
                sortino_ratio=results.get('sortino_ratio'),
                win_rate=results.get('win_rate'),
                max_drawdown=results.get('max_drawdown'),
                volatility=results.get('volatility'),
                total_trades=results.get('total_trades', 0),
                winning_trades=results.get('winning_trades', 0),
                losing_trades=results.get('losing_trades', 0),
                avg_trade_return=results.get('avg_trade_return'),
                avg_winning_trade=results.get('avg_winning_trade'),
                avg_losing_trade=results.get('avg_losing_trade'),
                value_at_risk_95=results.get('value_at_risk_95'),
                calmar_ratio=results.get('calmar_ratio'),
                benchmark_return=results.get('benchmark_return'),
                alpha=results.get('alpha'),
                beta=results.get('beta'),
                backtest_start_date=results.get('backtest_start_date'),
                backtest_end_date=results.get('backtest_end_date')
            )
            
            # Create individual trade logs
            trade_log = results.get('trade_log', [])
            for trade in trade_log:
                TradeLog.objects.create(
                    backtest_result=backtest_result,
                    security=trade['security'],
                    trade_type=trade['type'],
                    date=trade['date'],
                    price=trade['price'],
                    quantity=trade['quantity'],
                    commission=trade['commission'],
                    signal_value=trade.get('signal_value'),
                    notes=f"Auto-generated from mean reversion strategy"
                )
            
            logger.info(f"Backtest completed successfully for strategy {instance.name}")
            
        except Exception as e:
            logger.error(f"Error running backtest for strategy {instance.name}: {str(e)}")
            # Create a minimal result to indicate failure
            BacktestResult.objects.create(
                strategy=instance,
                total_trades=0
            )