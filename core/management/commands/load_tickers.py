# management/commands/load_tickers.py

import yfinance as yf
from django.core.management.base import BaseCommand
from core.models import Security

SP500_TICKERS = [...]  # You can use a static list or fetch dynamically
DJI_TICKERS = ['AAPL', 'MSFT', 'UNH', 'JPM', 'V', 'HD', 'PG', 'GS', 'MRK', 'AMGN', 'CAT', 'MCD', 'CVX', 'HON', 'IBM', 'TRV', 'JNJ', 'AXP', 'VZ', 'WMT', 'NKE', 'DIS', 'INTC', 'BA', 'CSCO', 'MMM', 'DOW', 'CRM', 'WBA', 'KO']

class Command(BaseCommand):
    help = 'Load DJI and S&P500 tickers into the database'

    def handle(self, *args, **kwargs):
        tickers = set(SP500_TICKERS + DJI_TICKERS)
        for symbol in tickers:
            data = yf.Ticker(symbol).info
            Security.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': data.get('shortName', ''),
                    'market_cap': data.get('marketCap'),
                    'sector': data.get('sector'),
                }
            )
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(tickers)} tickers"))