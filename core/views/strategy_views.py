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
        form = StrategyForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Strategy created successfully.")
            return redirect('dashboard')
    else:
        form = StrategyForm(user=request.user)
    return render(request, 'strategies/strategy_create.html', {'form': form})

# Strategy Detail
@login_required
def strategy_detail(request, pk):
    strategy = get_object_or_404(Strategy, pk=pk, user=request.user)
    ticker = strategy.tickers.first().symbol if strategy.tickers.exists() else 'AAPL'
    chart_path = generate_strategy_chart(ticker, strategy.lookback_days, strategy.entry_threshold, 0.5)

    backtest = run_mean_reversion_backtest(ticker, strategy.lookback_days, strategy.entry_threshold, 0.5)

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
            return redirect('strategy_detail', pk=strategy.pk)
    else:
        form = StrategyForm(instance=strategy)
    return render(request, 'strategies/strategy_edit.html', {'form': form, 'strategy': strategy, 'title': 'Edit Strategy'})

# Rename Strategy
@require_POST
@login_required
def strategy_rename(request, pk):
    strategy = get_object_or_404(Strategy, pk=pk, user=request.user)
    new_name = request.POST.get("name", "").strip()
    if new_name:
        strategy.name = new_name
        strategy.save()
        messages.success(request, "Strategy name updated.")
    return redirect('dashboard')

# Delete Strategy
@login_required
def strategy_delete(request, pk):
    strategy = get_object_or_404(Strategy, pk=pk, user=request.user)
    if request.method == 'POST':
        strategy.delete()
        messages.success(request, 'Strategy deleted successfully!')
        return redirect('dashboard')  # ✅ this is the key change
    return render(request, 'strategies/strategy_delete.html', {'strategy': strategy})