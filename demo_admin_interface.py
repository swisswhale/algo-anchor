#!/usr/bin/env python
"""
Demo script to showcase Admin Interface functionality
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.append('/Users/swisswhale/code/ga/projects/algo-anchor')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'algoanchor_app.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Security, Strategy, BacktestResult, TradeLog, PriceData
from django.db.models import Count, Avg

def demo_admin_interface():
    """Demonstrate the admin interface capabilities"""
    
    print("🔧 AlgoAnchor Admin Interface Demo")
    print("=" * 50)
    
    # Users Analysis
    users = User.objects.all()
    superusers = users.filter(is_superuser=True)
    regular_users = users.filter(is_superuser=False)
    
    print(f"\n👥 User Management:")
    print(f"   • Total Users: {users.count()}")
    print(f"   • Superusers: {superusers.count()}")
    print(f"   • Regular Users: {regular_users.count()}")
    
    # Show users with strategy counts
    users_with_strategies = users.annotate(strategy_count=Count('strategy')).filter(strategy_count__gt=0)
    print(f"\n   Users with Strategies:")
    for user in users_with_strategies:
        print(f"     - {user.username}: {user.strategy_count} strategies")
    
    # Securities Analysis
    securities = Security.objects.all()
    active_securities = securities.filter(is_active=True)
    
    print(f"\n🎯 Securities Management:")
    print(f"   • Total Securities: {securities.count()}")
    print(f"   • Active Securities: {active_securities.count()}")
    
    # Show securities by sector
    sector_breakdown = securities.values('sector').annotate(count=Count('id')).order_by('-count')[:5]
    print(f"\n   Top Sectors:")
    for sector in sector_breakdown:
        sector_name = sector['sector'] or 'Unknown'
        print(f"     - {sector_name}: {sector['count']} securities")
    
    # Show securities by market cap category
    market_cap_breakdown = securities.values('market_cap_category').annotate(count=Count('id'))
    print(f"\n   Market Cap Distribution:")
    for cap in market_cap_breakdown:
        print(f"     - {cap['market_cap_category']}: {cap['count']} securities")
    
    # Strategies Analysis
    strategies = Strategy.objects.all()
    strategies_with_results = strategies.filter(backtestresult__isnull=False)
    
    print(f"\n📈 Strategy Management:")
    print(f"   • Total Strategies: {strategies.count()}")
    print(f"   • With Backtest Results: {strategies_with_results.count()}")
    
    # Show strategy parameters distribution
    lookback_stats = strategies.aggregate(
        avg_lookback=Avg('lookback_days'),
        avg_threshold=Avg('entry_threshold')
    )
    print(f"   • Average Lookback Days: {lookback_stats['avg_lookback']:.1f}")
    print(f"   • Average Entry Threshold: {lookback_stats['avg_threshold']:.2f}")
    
    # Backtest Results Analysis
    backtest_results = BacktestResult.objects.all()
    profitable_strategies = backtest_results.filter(cumulative_return__gt=0)
    
    print(f"\n📊 Backtest Results:")
    print(f"   • Total Backtest Results: {backtest_results.count()}")
    print(f"   • Profitable Strategies: {profitable_strategies.count()}")
    
    if backtest_results.exists():
        performance_stats = backtest_results.aggregate(
            avg_return=Avg('cumulative_return'),
            avg_sharpe=Avg('sharpe_ratio'),
            avg_win_rate=Avg('win_rate'),
            avg_trades=Avg('total_trades')
        )
        
        print(f"\n   Performance Statistics:")
        print(f"     - Average Return: {performance_stats['avg_return']:.2f}%")
        print(f"     - Average Sharpe Ratio: {performance_stats['avg_sharpe']:.3f}")
        print(f"     - Average Win Rate: {performance_stats['avg_win_rate']:.1f}%")
        print(f"     - Average Trades per Strategy: {performance_stats['avg_trades']:.0f}")
    
    # Trade Log Analysis
    trades = TradeLog.objects.all()
    buy_trades = trades.filter(trade_type='BUY')
    sell_trades = trades.filter(trade_type='SELL')
    
    print(f"\n📝 Trade Log Analysis:")
    print(f"   • Total Trades: {trades.count()}")
    print(f"   • Buy Trades: {buy_trades.count()}")
    print(f"   • Sell Trades: {sell_trades.count()}")
    
    # Price Data Analysis
    price_data_count = PriceData.objects.count()
    unique_securities_with_data = PriceData.objects.values('security').distinct().count()
    
    print(f"\n💹 Price Data:")
    print(f"   • Total Price Records: {price_data_count}")
    print(f"   • Securities with Price Data: {unique_securities_with_data}")
    
    # Admin Features Summary
    print(f"\n🛠️  Admin Interface Features:")
    print(f"   ✅ Enhanced User Management")
    print(f"      - User profiles with strategy counts")
    print(f"      - Inline strategy display")
    print(f"      - Enhanced user listing")
    print(f"   ")
    print(f"   ✅ Securities Administration")
    print(f"      - Market cap formatting and categorization")
    print(f"      - Sector and exchange filtering")
    print(f"      - Strategy usage tracking")
    print(f"      - Bulk editing capabilities")
    print(f"   ")
    print(f"   ✅ Strategy Management")
    print(f"      - Performance summary display")
    print(f"      - Backtest status indicators") 
    print(f"      - Ticker relationship management")
    print(f"      - User filtering and search")
    print(f"   ")
    print(f"   ✅ Backtest Results Dashboard")
    print(f"      - Color-coded performance metrics")
    print(f"      - Trade log integration")
    print(f"      - Risk metrics display")
    print(f"      - Benchmark comparison")
    print(f"   ")
    print(f"   ✅ Trade Log Tracking")
    print(f"      - Detailed trade analysis")
    print(f"      - P&L visualization")
    print(f"      - Strategy performance linking")
    print(f"      - Date-based filtering")
    
    print(f"\n🌐 Admin Interface URL: http://127.0.0.1:8000/admin/")
    print(f"   Login with superuser credentials to access all features")

if __name__ == "__main__":
    demo_admin_interface()
