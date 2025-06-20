import yfinance as yf
from django.core.management.base import BaseCommand
from core.models import Security
import time
import requests
from bs4 import BeautifulSoup

# Major indices tickers for quick loading
DJI_TICKERS = [
    'AAPL', 'MSFT', 'UNH', 'JPM', 'V', 'HD', 'PG', 'GS', 'MRK', 'AMGN', 
    'CAT', 'MCD', 'CVX', 'HON', 'IBM', 'TRV', 'JNJ', 'AXP', 'VZ', 'WMT', 
    'NKE', 'DIS', 'INTC', 'BA', 'CSCO', 'MMM', 'DOW', 'CRM', 'WBA', 'KO'
]

# Popular technology stocks
TECH_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA', 
    'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'PYPL', 'SHOP', 
    'ZOOM', 'UBER', 'LYFT', 'TWTR', 'SNAP', 'SQ', 'ROKU', 'SPOT'
]

# Major financial stocks
FINANCIAL_TICKERS = [
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB',
    'PNC', 'TFC', 'COF', 'BK', 'STT', 'FITB', 'RF', 'KEY', 'CFG', 'ZION'
]

class Command(BaseCommand):
    help = 'Load popular tickers into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            choices=['dji', 'tech', 'financial', 'sp500', 'all'],
            default='all',
            help='Which ticker list to load'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of tickers to load'
        )

    def handle(self, *args, **options):
        source = options['source']
        limit = options['limit']
        
        if source == 'dji':
            tickers = DJI_TICKERS
        elif source == 'tech':
            tickers = TECH_TICKERS
        elif source == 'financial':
            tickers = FINANCIAL_TICKERS
        elif source == 'sp500':
            tickers = self.get_sp500_tickers()
        else:  # all
            tickers = list(set(DJI_TICKERS + TECH_TICKERS + FINANCIAL_TICKERS))
        
        # Limit the number of tickers
        tickers = tickers[:limit]
        
        self.stdout.write(f"Loading {len(tickers)} tickers from {source}...")
        
        loaded_count = 0
        failed_count = 0
        
        for i, symbol in enumerate(tickers, 1):
            try:
                self.stdout.write(f"Processing {symbol} ({i}/{len(tickers)})...")
                
                # Fetch data from yfinance
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Create or update security
                security, created = Security.objects.update_or_create(
                    symbol=symbol,
                    defaults={
                        'name': info.get('longName') or info.get('shortName') or '',
                        'sector': info.get('sector', ''),
                        'industry': info.get('industry', ''),
                        'market_cap': info.get('marketCap'),
                        'exchange': self.get_exchange_from_info(info),
                        'currency': info.get('currency', 'USD'),
                        'is_active': True,
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ Created {symbol} - {security.name}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  ↻ Updated {symbol} - {security.name}")
                    )
                
                loaded_count += 1
                
                # Rate limiting to avoid overwhelming Yahoo Finance
                time.sleep(0.5)
                
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Failed to load {symbol}: {str(e)}")
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted! Loaded: {loaded_count}, Failed: {failed_count}"
            )
        )

    def get_exchange_from_info(self, info):
        """Determine exchange from yfinance info"""
        exchange = info.get('exchange', '').upper()
        if 'NYSE' in exchange:
            return 'NYSE'
        elif 'NASDAQ' in exchange:
            return 'NASDAQ'
        elif 'AMEX' in exchange:
            return 'AMEX'
        else:
            return 'OTHER'

    def get_sp500_tickers(self):
        """Fetch S&P 500 tickers from Wikipedia"""
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'id': 'constituents'})
            tickers = []
            
            for row in table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all('td')
                if cells:
                    ticker = cells[0].text.strip()
                    tickers.append(ticker)
            
            self.stdout.write(f"Found {len(tickers)} S&P 500 tickers")
            return tickers
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Could not fetch S&P 500 list: {e}")
            )
            # Fallback to a smaller predefined list
            return DJI_TICKERS + TECH_TICKERS[:20]