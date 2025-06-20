from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Strategy, BacktestResult
from django.db.models import Count

def home(request):
    """Public home page"""
    return render(request, 'home.html')

@login_required
def dashboard(request):
    """Dashboard showing user's strategies with performance data"""
    strategies = Strategy.objects.filter(user=request.user).select_related('backtestresult').prefetch_related('tickers').order_by('-created_at')
    
    # Calculate summary statistics
    total_strategies = strategies.count()
    strategies_with_results = strategies.filter(backtestresult__isnull=False).count()
    
    context = {
        'strategies': strategies,
        'total_strategies': total_strategies,
        'strategies_with_results': strategies_with_results,
    }
    return render(request, 'dashboard.html', context)