#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'algoanchor_app.settings')
django.setup()

from core.forms import StrategyForm
from django.contrib.auth.models import User

# Get a user
user = User.objects.first()
if not user:
    user = User.objects.create_user('testuser', 'test@example.com', 'password123')

# Test form data
form_data = {
    'name': 'Test Strategy Debug',
    'lookback_days': 20,
    'entry_threshold': -2.0,
    'exit_rule': 'mean_revert',
    'tickers': 'AAPL, MSFT'
}

print("Creating form with data:", form_data)
form = StrategyForm(data=form_data)

if form.is_valid():
    print("Form is valid!")
    print("=" * 50)
    
    # Simulate the view's behavior
    strategy = form.save(commit=False)
    strategy.user = user
    strategy.save()
    print("Strategy saved with ID:", strategy.id)
    
    print("Calling form.save_m2m()...")
    form.save_m2m()
    
    print("=" * 50)
    print(f"Final strategy ticker count: {strategy.tickers.count()}")
    print(f"Tickers: {[t.symbol for t in strategy.tickers.all()]}")
    
else:
    print("Form errors:", form.errors)
