from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from core.models import Strategy
from core.forms import StrategyForm
from core.utils.charting import generate_strategy_chart_html, generate_trade_markers_data
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import logging

logger = logging.getLogger(__name__)

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
            
            # Manually handle ticker assignment since it's a custom field
            if hasattr(strategy, '_pending_tickers'):
                strategy.tickers.set(strategy._pending_tickers)
                del strategy._pending_tickers
                
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
    
    # Generate comprehensive charts and analytics
    price_chart_html = None
    performance_chart_html = None
    stats = {}
    trade_markers = []
    
    try:
        if strategy.tickers.exists():
            # Generate interactive charts
            price_chart_html, performance_chart_html, stats = generate_strategy_chart_html(strategy)
            
            # Generate trade markers for overlay
            trade_markers = generate_trade_markers_data(strategy)
            
            if price_chart_html:
                messages.success(request, "Charts generated successfully!")
            else:
                messages.warning(request, "Unable to generate charts - insufficient data or network issues.")
                
    except Exception as e:
        logger.error(f"Error generating charts for strategy {strategy.name}: {str(e)}")
        messages.error(request, "Chart generation failed. Please try again later.")

    context = {
        'strategy': strategy,
        'price_chart_html': price_chart_html,
        'performance_chart_html': performance_chart_html,
        'stats': stats,
        'trade_markers': trade_markers,
        'has_charts': price_chart_html is not None,
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
    
    # If GET request, show the confirmation page
    return render(request, 'strategies/delete.html', {'strategy': strategy})