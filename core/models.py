from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Security(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

class PriceData(models.Model):
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
    date = models.DateField()
    close = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('security', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.security.symbol} - {self.date} - {self.close}"

class Strategy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    lookback_days = models.IntegerField()
    entry_threshold = models.FloatField(help_text="Z-score threshold for entry")
    exit_rule = models.CharField(max_length=100)  # e.g. "mean", "halfway"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class BacktestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_return = models.FloatField()
    win_rate = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Backtest: {self.strategy.name} on {self.security.symbol}"

class Trade(models.Model):
    backtest = models.ForeignKey(BacktestResult, on_delete=models.CASCADE)
    entry_date = models.DateField()
    exit_date = models.DateField()
    entry_price = models.DecimalField(max_digits=10, decimal_places=2)
    exit_price = models.DecimalField(max_digits=10, decimal_places=2)
    return_pct = models.FloatField()

    def __str__(self):
        return f"Trade {self.entry_date} → {self.exit_date} | {self.return_pct:.2f}%"