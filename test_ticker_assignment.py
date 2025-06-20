#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.append('/Users/swisswhale/code/ga/projects/algo-anchor')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'algoanchor_app.settings')
django.setup()

from django.contrib.auth.models import User
from core.forms import StrategyForm
from core.models import Strategy

def test_form_assignment():
    print("=== Testing Form Ticker Assignment ===")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(username='testuser', defaults={'email': 'test@example.com'})
    if created:
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Simulate form data
    form_data = {
        'name': 'Test Strategy',
        'lookback_days': 20,
        'entry_threshold': -2.0,
        'exit_rule': 'mean_revert',
        'tickers': 'AAPL,MSFT'
    }
    
    print(f"Form data: {form_data}")
    
    # Create and validate form
    form = StrategyForm(data=form_data)
    print(f"Form is valid: {form.is_valid()}")
    
    if not form.is_valid():
        print(f"Form errors: {form.errors}")
        return
    
    print(f"Cleaned tickers: {form.cleaned_data['tickers']}")
    
    # Test the exact same process as the view
    print("\n=== Simulating View Logic ===")
    strategy = form.save(commit=False)
    print(f"Strategy created (not yet saved): {strategy.name}")
    try:
        print(f"Strategy user before assignment: {strategy.user}")
    except:
        print("Strategy user before assignment: None (not yet assigned)")
    print(f"Strategy pk before save: {strategy.pk}")
    print(f"Has _pending_tickers: {hasattr(strategy, '_pending_tickers')}")
    if hasattr(strategy, '_pending_tickers'):
        print(f"Pending tickers: {[s.symbol for s in strategy._pending_tickers]}")
    
    strategy.user = user
    print(f"Strategy user after assignment: {strategy.user}")
    
    strategy.save()
    print(f"Strategy saved with pk: {strategy.pk}")
    print(f"Tickers count after save: {strategy.tickers.count()}")
    
    # Call save_m2m
    print("\n=== Calling form.save_m2m() ===")
    form.save_m2m()
    
    # Manually handle ticker assignment like the updated view
    print("\n=== Manual ticker assignment ===")
    if hasattr(strategy, '_pending_tickers'):
        print(f"Found pending tickers: {[s.symbol for s in strategy._pending_tickers]}")
        strategy.tickers.set(strategy._pending_tickers)
        print(f"Assigned tickers manually, count: {strategy.tickers.count()}")
        del strategy._pending_tickers
    else:
        print("No pending tickers found")
    
    print(f"Final tickers count: {strategy.tickers.count()}")
    if strategy.tickers.exists():
        print(f"Final tickers: {[t.symbol for t in strategy.tickers.all()]}")
    else:
        print("No tickers found!")
    
    # Clean up
    strategy.delete()
    print("\nTest strategy deleted.")

if __name__ == '__main__':
    test_form_assignment()
