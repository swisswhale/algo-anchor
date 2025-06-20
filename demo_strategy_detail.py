#!/usr/bin/env python
"""
Demo script to showcase Strategy Detail View functionality
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.append('/Users/swisswhale/code/ga/projects/algo-anchor')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'algoanchor_app.settings')
django.setup()

from core.models import Strategy, Security
from core.utils.charting import generate_strategy_chart_html, generate_trade_markers_data
from django.contrib.auth.models import User

def demo_strategy_detail():
    """Demonstrate the strategy detail view functionality"""
    
    print("🔍 Strategy Detail View Demo")
    print("=" * 50)
    
    # Get a sample strategy
    strategies = Strategy.objects.all()
    if not strategies.exists():
        print("❌ No strategies found. Please create a strategy first.")
        return
    
    strategy = strategies.first()
    print(f"📈 Analyzing Strategy: {strategy.name}")
    print(f"   User: {strategy.user.username}")
    print(f"   Lookback Days: {strategy.lookback_days}")
    print(f"   Entry Threshold: {strategy.entry_threshold}")
    print(f"   Exit Rule: {strategy.exit_rule}")
    
    # Check tickers
    tickers = strategy.tickers.all()
    print(f"\n🎯 Securities ({tickers.count()}):")
    for ticker in tickers:
        print(f"   • {ticker.symbol} - {ticker.name or 'N/A'}")
        if ticker.sector:
            print(f"     Sector: {ticker.sector}")
        if ticker.market_cap:
            print(f"     Market Cap: ${ticker.market_cap:,.0f}")
    
    # Check backtest results
    if hasattr(strategy, 'backtestresult') and strategy.backtestresult:
        br = strategy.backtestresult
        print(f"\n📊 Backtest Results:")
        print(f"   • Cumulative Return: {br.cumulative_return:.2f}%")
        if br.sharpe_ratio:
            print(f"   • Sharpe Ratio: {br.sharpe_ratio:.3f}")
        if br.win_rate:
            print(f"   • Win Rate: {br.win_rate:.1f}%")
        if br.max_drawdown:
            print(f"   • Max Drawdown: {br.max_drawdown:.2f}%")
    
    # Test chart generation
    print(f"\n📈 Chart Generation Test:")
    try:
        if tickers.exists():
            print("   Generating interactive charts...")
            price_chart, performance_chart, stats = generate_strategy_chart_html(strategy)
            
            if price_chart:
                print("   ✅ Price chart with signals generated successfully")
                print("   ✅ Performance comparison chart generated")
                
                # Show some stats
                if stats:
                    print(f"\n📊 Technical Analysis:")
                    print(f"   • Current Z-Score: {stats.get('current_z_score', 'N/A')}")
                    print(f"   • Price Volatility: {stats.get('price_volatility', 'N/A')}")
                    print(f"   • Data Points: {stats.get('data_points', 'N/A')}")
                    
            else:
                print("   ⚠️  Chart generation returned empty (may be network/data issue)")
                
            # Test trade markers
            trade_markers = generate_trade_markers_data(strategy)
            print(f"   📍 Trade markers generated: {len(trade_markers)} historical trades")
            
        else:
            print("   ⚠️  No tickers assigned - charts cannot be generated")
            
    except Exception as e:
        print(f"   ❌ Chart generation failed: {str(e)}")
    
    print(f"\n🌐 Strategy Detail URL: http://127.0.0.1:8000/strategies/{strategy.pk}/")
    print("\n✨ Strategy Detail View Features:")
    print("   • Interactive Plotly price charts with signals")
    print("   • Z-score analysis and Bollinger bands")
    print("   • Performance comparison vs buy & hold")
    print("   • Technical statistics and indicators")
    print("   • Trade markers with entry/exit points")
    print("   • Responsive design with Bootstrap UI")

if __name__ == "__main__":
    demo_strategy_detail()
