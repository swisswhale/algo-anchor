from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from core.models import Strategy
from core.forms import StrategyForm
from core.utils.charting import generate_strategy_chart
from core.utils.backtest import run_mean_reversion_backtest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# Strategy List
@login_required
def strategy_list(request):
    """Display list of strategies"""
    return render(request, 'strategies/list.html')

# Create Strategy
@login_required
def strategy_create(request):
    if request.method == 'POST':
        form = StrategyForm(request.POST)
        if form.is_valid():
            strategy = form.save(commit=False)
            strategy.user = request.user
            strategy.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, f"Strategy '{strategy.name}' created successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StrategyForm()
    return render(request, 'strategies/create.html', {'form': form})

# Strategy Detail
@login_required
def strategy_detail(request, pk):
    strategy = get_object_or_404(Strategy, pk=pk, user=request.user)
    
    # Safely handle chart generation (will be implemented in Step 6)
    chart_path = None
    backtest = None
    
    try:
        if strategy.tickers.exists():
            ticker = strategy.tickers.first().symbol
            # Temporarily disable chart generation to avoid errors
            # chart_path = generate_strategy_chart(ticker, strategy.lookback_days, strategy.entry_threshold, 0.5)
            # backtest = run_mean_reversion_backtest(ticker, strategy.lookback_days, strategy.entry_threshold, 0.5)
    except Exception as e:
        messages.warning(request, "Chart generation temporarily unavailable.")

    context = {
        'strategy': strategy,
        'chart_path': chart_path,
        'backtest': backtest,
    }
    return render(request, 'strategies/detail.html', context)

# Edit Strategy
@login_required
def strategy_edit(request, pk):
    strategy = get_object_or_404(Strategy, pk=pk, user=request.user)
    if request.method == 'POST':
        form = StrategyForm(request.POST, instance=strategy)
        if form.is_valid():
            form.save()
            messages.success(request, f"Strategy '{strategy.name}' updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StrategyForm(instance=strategy)
    return render(request, 'strategies/edit.html', {'form': form, 'strategy': strategy})

# Rename Strategy
@require_POST
@login_required
def strategy_rename(request, pk):
    strategy = get_object_or_404(Strategy, pk=pk, user=request.user)
    new_name = request.POST.get("name", "").strip()
    if new_name and new_name != strategy.name:
        old_name = strategy.name
        strategy.name = new_name
        strategy.save()
        messages.success(request, f"Strategy renamed from '{old_name}' to '{new_name}'")
    return redirect('dashboard')

# Delete Strategy
@login_required
def strategy_delete(request, pk):
    strategy = get_object_or_404(Strategy, pk=pk, user=request.user)
    if request.method == 'POST':
        strategy_name = strategy.name
        strategy.delete()
        messages.success(request, f"Strategy '{strategy_name}' deleted successfully!")
        return redirect('dashboard')
    return render(request, 'strategies/delete.html', {'strategy': strategy})