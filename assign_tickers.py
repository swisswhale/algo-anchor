#!/usr/bin/env python
"""
Script to assign default tickers to strategies that don't have any
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'algoanchor_app.settings')
django.setup()

from core.models import Strategy, Security
import random

def assign_default_tickers():
    """Assign default tickers to strategies that don't have any"""
    
    # Get available tickers
    available_tickers = list(Security.objects.all())
    if not available_tickers:
        print("No tickers available in database")
        return
    
    # Get strategies without tickers
    strategies_without_tickers = []
    for strategy in Strategy.objects.all():
        if not strategy.tickers.exists():
            strategies_without_tickers.append(strategy)
    
    print(f"Found {len(strategies_without_tickers)} strategies without tickers")
    print(f"Available tickers: {len(available_tickers)}")
    
    # Popular tickers to prefer for assignment
    popular_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'SPY']
    popular_tickers = [t for t in available_tickers if t.symbol in popular_symbols]
    
    for strategy in strategies_without_tickers:
        # Assign 1-3 random tickers from popular ones if available, otherwise from all
        tickers_to_assign = popular_tickers if popular_tickers else available_tickers
        num_tickers = random.randint(1, min(3, len(tickers_to_assign)))
        selected_tickers = random.sample(tickers_to_assign, num_tickers)
        
        strategy.tickers.set(selected_tickers)
        ticker_symbols = [t.symbol for t in selected_tickers]
        print(f"✓ Assigned {ticker_symbols} to '{strategy.name}' (ID: {strategy.id})")

if __name__ == "__main__":
    assign_default_tickers()
    print("\nTicker assignment completed!")
