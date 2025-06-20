#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'algoanchor_app.settings')
django.setup()

from core.forms import StrategyForm
from django.contrib.auth.models import User

# Check method resolution order
print("StrategyForm MRO:", StrategyForm.__mro__)
print("save_m2m method location:", StrategyForm.save_m2m)
print("Has custom save_m2m:", hasattr(StrategyForm, 'save_m2m'))

# Get a user
user = User.objects.first()

# Test form data
form_data = {
    'name': 'Test Strategy Debug 2',
    'lookback_days': 20,
    'entry_threshold': -2.0,
    'exit_rule': 'mean_revert',
    'tickers': 'AAPL, MSFT'
}

form = StrategyForm(data=form_data)

if form.is_valid():
    print("Form is valid!")
    print("Form's save_m2m method:", form.save_m2m)
    
    # Simulate the view's behavior
    strategy = form.save(commit=False)
    strategy.user = user
    strategy.save()
    
    print("About to call save_m2m...")
    try:
        form.save_m2m()
        print("save_m2m completed successfully")
    except Exception as e:
        print(f"Error in save_m2m: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"Final strategy ticker count: {strategy.tickers.count()}")
    print(f"Tickers: {[t.symbol for t in strategy.tickers.all()]}")
    
else:
    print("Form errors:", form.errors)
