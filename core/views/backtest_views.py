"""
Backtest-related views for AlgoAnchor
Provides views for displaying and managing backtest results.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from core.models import Strategy, BacktestResult, TradeLog
from core.services.backtest_engine import run_comprehensive_backtest
import logging

logger = logging.getLogger(__name__)


@login_required
def backtest_detail(request, strategy_id):
    """Display detailed backtest results for a strategy"""
    strategy = get_object_or_404(Strategy, id=strategy_id, user=request.user)
    
    try:
        backtest_result = strategy.backtestresult
    except BacktestResult.DoesNotExist:
        backtest_result = None
    
    # Get trade log with pagination
    trades = []
    if backtest_result:
        trades_qs = TradeLog.objects.filter(backtest_result=backtest_result)
        paginator = Paginator(trades_qs, 25)  # 25 trades per page
        page_number = request.GET.get('page')
        trades = paginator.get_page(page_number)
    
    context = {
        'strategy': strategy,
        'backtest_result': backtest_result,
        'trades': trades,
        'has_results': backtest_result is not None,
    }
    
    return render(request, 'backtests/detail.html', context)


@login_required
def rerun_backtest(request, strategy_id):
    """Re-run backtest for a strategy (AJAX endpoint)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    strategy = get_object_or_404(Strategy, id=strategy_id, user=request.user)
    
    try:
        # Delete existing results
        BacktestResult.objects.filter(strategy=strategy).delete()
        
        # Run new backtest
        results = run_comprehensive_backtest(strategy)
        
        if not results:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate backtest results'
            })
        
        # Create new BacktestResult
        backtest_result = BacktestResult.objects.create(
            strategy=strategy,
            cumulative_return=results.get('cumulative_return'),
            annualized_return=results.get('annualized_return'),
            sharpe_ratio=results.get('sharpe_ratio'),
            sortino_ratio=results.get('sortino_ratio'),
            win_rate=results.get('win_rate'),
            max_drawdown=results.get('max_drawdown'),
            volatility=results.get('volatility'),
            total_trades=results.get('total_trades', 0),
            winning_trades=results.get('winning_trades', 0),
            losing_trades=results.get('losing_trades', 0),
            avg_trade_return=results.get('avg_trade_return'),
            avg_winning_trade=results.get('avg_winning_trade'),
            avg_losing_trade=results.get('avg_losing_trade'),
            value_at_risk_95=results.get('value_at_risk_95'),
            calmar_ratio=results.get('calmar_ratio'),
            benchmark_return=results.get('benchmark_return'),
            alpha=results.get('alpha'),
            beta=results.get('beta'),
            backtest_start_date=results.get('backtest_start_date'),
            backtest_end_date=results.get('backtest_end_date')
        )
        
        # Create trade logs
        trade_log = results.get('trade_log', [])
        for trade in trade_log:
            TradeLog.objects.create(
                backtest_result=backtest_result,
                security=trade['security'],
                trade_type=trade['type'],
                date=trade['date'],
                price=trade['price'],
                quantity=trade['quantity'],
                commission=trade['commission'],
                signal_value=trade.get('signal_value'),
                notes="Manually re-run by user"
            )
        
        return JsonResponse({
            'success': True,
            'results': backtest_result.get_performance_summary(),
            'message': 'Backtest completed successfully'
        })
        
    except Exception as e:
        logger.error(f'Error re-running backtest for strategy {strategy.name}: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'Backtest failed: {str(e)}'
        })


@login_required
def backtest_api(request, strategy_id):
    """API endpoint to get backtest results as JSON"""
    strategy = get_object_or_404(Strategy, id=strategy_id, user=request.user)
    
    try:
        backtest_result = strategy.backtestresult
        
        # Get recent trades
        recent_trades = TradeLog.objects.filter(
            backtest_result=backtest_result
        ).order_by('-date')[:10]
        
        trade_data = []
        for trade in recent_trades:
            trade_data.append({
                'date': trade.date.isoformat(),
                'type': trade.trade_type,
                'symbol': trade.security.symbol,
                'price': trade.price,
                'quantity': trade.quantity,
                'pnl': trade.pnl,
                'signal_value': trade.signal_value,
            })
        
        return JsonResponse({
            'strategy': {
                'name': strategy.name,
                'lookback_days': strategy.lookback_days,
                'entry_threshold': strategy.entry_threshold,
                'exit_threshold': strategy.exit_threshold,
            },
            'performance': {
                'cumulative_return': backtest_result.cumulative_return,
                'annualized_return': backtest_result.annualized_return,
                'sharpe_ratio': backtest_result.sharpe_ratio,
                'sortino_ratio': backtest_result.sortino_ratio,
                'win_rate': backtest_result.win_rate,
                'max_drawdown': backtest_result.max_drawdown,
                'volatility': backtest_result.volatility,
                'total_trades': backtest_result.total_trades,
                'winning_trades': backtest_result.winning_trades,
                'losing_trades': backtest_result.losing_trades,
                'value_at_risk_95': backtest_result.value_at_risk_95,
                'calmar_ratio': backtest_result.calmar_ratio,
                'alpha': backtest_result.alpha,
                'beta': backtest_result.beta,
            },
            'trades': trade_data,
            'backtest_period': {
                'start_date': backtest_result.backtest_start_date.isoformat() if backtest_result.backtest_start_date else None,
                'end_date': backtest_result.backtest_end_date.isoformat() if backtest_result.backtest_end_date else None,
            }
        })
        
    except BacktestResult.DoesNotExist:
        return JsonResponse({
            'error': 'No backtest results found for this strategy'
        }, status=404)


@login_required
def compare_strategies(request):
    """Compare multiple strategies' backtest results"""
    user_strategies = Strategy.objects.filter(
        user=request.user,
        backtestresult__isnull=False
    ).select_related('backtestresult')
    
    # Get strategy IDs to compare from query params
    strategy_ids = request.GET.getlist('strategies')
    if strategy_ids:
        user_strategies = user_strategies.filter(id__in=strategy_ids)
    
    comparison_data = []
    for strategy in user_strategies:
        result = strategy.backtestresult
        comparison_data.append({
            'strategy': strategy,
            'performance': result.get_performance_summary(),
            'metrics': {
                'cumulative_return': result.cumulative_return,
                'sharpe_ratio': result.sharpe_ratio,
                'max_drawdown': result.max_drawdown,
                'total_trades': result.total_trades,
                'win_rate': result.win_rate,
            }
        })
    
    context = {
        'comparison_data': comparison_data,
        'all_strategies': Strategy.objects.filter(user=request.user),
    }
    
    return render(request, 'backtests/compare.html', context)
