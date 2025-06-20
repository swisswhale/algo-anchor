from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from .models import Security, Strategy, PriceData, BacktestResult, TradeLog


# Admin Site Configuration
admin.site.site_header = "AlgoAnchor Administration"
admin.site.site_title = "AlgoAnchor Admin"
admin.site.index_title = "Welcome to AlgoAnchor Administration"


# Custom Admin Actions
def activate_securities(modeladmin, request, queryset):
    """Bulk action to activate securities"""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f'{updated} securities were activated.')
activate_securities.short_description = "Activate selected securities"

def deactivate_securities(modeladmin, request, queryset):
    """Bulk action to deactivate securities"""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f'{updated} securities were deactivated.')
deactivate_securities.short_description = "Deactivate selected securities"

def rerun_backtests(modeladmin, request, queryset):
    """Bulk action to rerun backtests for selected strategies"""
    from .services.backtest_engine import run_comprehensive_backtest
    
    count = 0
    for strategy in queryset:
        try:
            # Delete existing backtest result
            if hasattr(strategy, 'backtestresult'):
                strategy.backtestresult.delete()
            
            # Rerun backtest
            results = run_comprehensive_backtest(strategy)
            if results:
                count += 1
        except Exception as e:
            pass  # Continue with other strategies
    
    modeladmin.message_user(request, f'Backtests rerun for {count} strategies.')
rerun_backtests.short_description = "Rerun backtests for selected strategies"


# Security Admin
@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    list_display = [
        'symbol', 'name', 'sector', 'market_cap_display', 
        'market_cap_category', 'exchange', 'is_active', 'strategy_count'
    ]
    list_filter = [
        'market_cap_category', 'exchange', 'sector', 'is_active', 'created_at'
    ]
    search_fields = ['symbol', 'name', 'sector', 'industry']
    list_editable = ['is_active']
    readonly_fields = ['market_cap_category', 'last_updated', 'created_at']
    actions = [activate_securities, deactivate_securities]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('symbol', 'name', 'exchange', 'currency', 'is_active')
        }),
        ('Company Details', {
            'fields': ('sector', 'industry', 'market_cap', 'market_cap_category')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated'),
            'classes': ('collapse',)
        })
    )
    
    def market_cap_display(self, obj):
        """Display formatted market cap"""
        return obj.get_market_cap_display_value()
    market_cap_display.short_description = 'Market Cap'
    market_cap_display.admin_order_field = 'market_cap'
    
    def strategy_count(self, obj):
        """Count of strategies using this security"""
        count = obj.strategies.count()
        if count > 0:
            url = reverse('admin:core_strategy_changelist') + f'?tickers__id__exact={obj.id}'
            return format_html('<a href="{}">{} strategies</a>', url, count)
        return "0 strategies"
    strategy_count.short_description = 'Used in Strategies'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('strategies')


# Strategy Admin
@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'tickers_display', 'lookback_days', 
        'entry_threshold', 'has_backtest', 'performance_summary', 'created_at'
    ]
    list_filter = [
        'user', 'lookback_days', 'created_at', 'tickers__sector'
    ]
    search_fields = ['name', 'user__username', 'tickers__symbol']
    filter_horizontal = ['tickers']
    readonly_fields = ['created_at', 'updated_at']
    actions = [rerun_backtests]
    
    fieldsets = (
        ('Strategy Details', {
            'fields': ('name', 'user', 'tickers')
        }),
        ('Parameters', {
            'fields': ('lookback_days', 'entry_threshold', 'exit_rule')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def tickers_display(self, obj):
        """Display ticker symbols"""
        tickers = obj.get_tickers_display()
        return tickers if tickers else "No tickers"
    tickers_display.short_description = 'Tickers'
    
    def has_backtest(self, obj):
        """Show if strategy has backtest results"""
        if obj.has_backtest_results():
            url = reverse('admin:core_backtestresult_change', args=[obj.backtestresult.id])
            return format_html('<a href="{}">✅ View Results</a>', url)
        return "❌ No Results"
    has_backtest.short_description = 'Backtest Status'
    
    def performance_summary(self, obj):
        """Display key performance metrics"""
        summary = obj.get_performance_summary()
        if summary:
            return format_html(
                'Return: {:.2f}% | Sharpe: {:.2f} | Win Rate: {:.1f}%',
                summary['return'] or 0,
                summary['sharpe'] or 0,
                summary['win_rate'] or 0
            )
        return "No data"
    performance_summary.short_description = 'Performance'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('tickers', 'backtestresult')
    
    # Custom Admin Actions
    def rerun_backtests(modeladmin, request, queryset):
        """Bulk action to rerun backtests for selected strategies"""
        from .services.backtest_engine import run_comprehensive_backtest
        
        count = 0
        for strategy in queryset:
            try:
                # Delete existing backtest result
                if hasattr(strategy, 'backtestresult'):
                    strategy.backtestresult.delete()
                
                # Rerun backtest
                results = run_comprehensive_backtest(strategy)
                if results:
                    count += 1
            except Exception as e:
                pass  # Continue with other strategies
        
        modeladmin.message_user(request, f'Backtests rerun for {count} strategies.')
    rerun_backtests.short_description = "Rerun backtests for selected strategies"


# PriceData Admin
@admin.register(PriceData)
class PriceDataAdmin(admin.ModelAdmin):
    list_display = ['security', 'date', 'close']
    list_filter = ['security', 'date']
    search_fields = ['security__symbol', 'security__name']
    date_hierarchy = 'date'
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('security')


# BacktestResult Admin
@admin.register(BacktestResult)
class BacktestResultAdmin(admin.ModelAdmin):
    list_display = [
        'strategy_name', 'user', 'cumulative_return_display', 
        'sharpe_ratio', 'win_rate_display', 'max_drawdown_display',
        'total_trades', 'trade_log_link', 'created_at'
    ]
    list_filter = [
        'strategy__user', 'created_at', 'backtest_start_date'
    ]
    search_fields = ['strategy__name', 'strategy__user__username']
    readonly_fields = [
        'strategy', 'created_at', 'updated_at', 'trade_summary'
    ]
    
    fieldsets = (
        ('Strategy Information', {
            'fields': ('strategy', 'backtest_start_date', 'backtest_end_date')
        }),
        ('Performance Metrics', {
            'fields': (
                'cumulative_return', 'annualized_return', 'sharpe_ratio', 
                'sortino_ratio', 'volatility'
            )
        }),
        ('Trade Statistics', {
            'fields': (
                'total_trades', 'winning_trades', 'losing_trades',
                'avg_trade_return', 'avg_winning_trade', 'avg_losing_trade'
            )
        }),
        ('Risk Metrics', {
            'fields': (
                'win_rate', 'max_drawdown', 'value_at_risk_95', 'calmar_ratio'
            )
        }),
        ('Benchmark Comparison', {
            'fields': ('benchmark_return', 'alpha', 'beta'),
            'classes': ('collapse',)
        }),
        ('Trade Summary', {
            'fields': ('trade_summary',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def strategy_name(self, obj):
        """Display strategy name with link"""
        url = reverse('admin:core_strategy_change', args=[obj.strategy.id])
        return format_html('<a href="{}">{}</a>', url, obj.strategy.name)
    strategy_name.short_description = 'Strategy'
    strategy_name.admin_order_field = 'strategy__name'
    
    def user(self, obj):
        """Display strategy user"""
        return obj.strategy.user.username
    user.short_description = 'User'
    user.admin_order_field = 'strategy__user__username'
    
    def cumulative_return_display(self, obj):
        """Display formatted cumulative return"""
        if obj.cumulative_return is not None:
            color = 'green' if obj.cumulative_return >= 0 else 'red'
            return format_html(
                '<span style="color: {};">{:.2f}%</span>',
                color, obj.cumulative_return
            )
        return "N/A"
    cumulative_return_display.short_description = 'Return'
    cumulative_return_display.admin_order_field = 'cumulative_return'
    
    def win_rate_display(self, obj):
        """Display formatted win rate"""
        if obj.win_rate is not None:
            color = 'green' if obj.win_rate >= 50 else 'orange' if obj.win_rate >= 30 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, obj.win_rate
            )
        return "N/A"
    win_rate_display.short_description = 'Win Rate'
    win_rate_display.admin_order_field = 'win_rate'
    
    def max_drawdown_display(self, obj):
        """Display formatted max drawdown"""
        if obj.max_drawdown is not None:
            return format_html(
                '<span style="color: red;">{:.2f}%</span>',
                obj.max_drawdown
            )
        return "N/A"
    max_drawdown_display.short_description = 'Max Drawdown'
    max_drawdown_display.admin_order_field = 'max_drawdown'
    
    def trade_log_link(self, obj):
        """Link to view trade log"""
        trade_count = obj.trades.count()
        if trade_count > 0:
            url = reverse('admin:core_tradelog_changelist') + f'?backtest_result__id__exact={obj.id}'
            return format_html('<a href="{}">{} trades</a>', url, trade_count)
        return "No trades"
    trade_log_link.short_description = 'Trade Log'
    
    def trade_summary(self, obj):
        """Display trade summary information"""
        if obj.trades.exists():
            trades = obj.trades.all()
            buy_trades = trades.filter(trade_type='BUY').count()
            sell_trades = trades.filter(trade_type='SELL').count()
            exit_trades = trades.filter(trade_type='EXIT').count()
            
            return format_html(
                '<strong>Trade Breakdown:</strong><br>'
                'Buy: {} | Sell: {} | Exit: {}<br>'
                '<strong>Performance:</strong><br>'
                'Win Rate: {:.1f}% | Total Trades: {}',
                buy_trades, sell_trades, exit_trades,
                obj.win_rate or 0, obj.total_trades
            )
        return "No trade data available"
    trade_summary.short_description = 'Trade Summary'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('strategy__user').prefetch_related('trades')


# TradeLog Admin
@admin.register(TradeLog)
class TradeLogAdmin(admin.ModelAdmin):
    list_display = [
        'strategy_name', 'security', 'trade_type', 'date', 
        'price', 'quantity', 'pnl_display', 'signal_value'
    ]
    list_filter = [
        'trade_type', 'security', 'backtest_result__strategy__user', 'date'
    ]
    search_fields = [
        'backtest_result__strategy__name', 'security__symbol', 
        'backtest_result__strategy__user__username'
    ]
    date_hierarchy = 'date'
    readonly_fields = ['backtest_result', 'created_at']
    list_per_page = 100
    
    fieldsets = (
        ('Trade Information', {
            'fields': ('backtest_result', 'security', 'trade_type', 'date')
        }),
        ('Execution Details', {
            'fields': ('price', 'quantity', 'commission', 'signal_value')
        }),
        ('Performance', {
            'fields': ('pnl', 'cumulative_pnl')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def strategy_name(self, obj):
        """Display strategy name"""
        return obj.backtest_result.strategy.name
    strategy_name.short_description = 'Strategy'
    strategy_name.admin_order_field = 'backtest_result__strategy__name'
    
    def pnl_display(self, obj):
        """Display formatted P&L"""
        if obj.pnl is not None:
            color = 'green' if obj.pnl >= 0 else 'red'
            return format_html(
                '<span style="color: {};">${:.2f}</span>',
                color, obj.pnl
            )
        return "N/A"
    pnl_display.short_description = 'P&L'
    pnl_display.admin_order_field = 'pnl'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'backtest_result__strategy', 'security'
        )


# Enhanced User Admin
class UserProfileInline(admin.StackedInline):
    """Inline for user profile information"""
    model = Strategy
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['name', 'lookback_days', 'entry_threshold', 'created_at']
    verbose_name = "Strategy"
    verbose_name_plural = "User Strategies"
    
    def has_add_permission(self, request, obj=None):
        return False


# Unregister the default User admin and register our custom one
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with strategy information"""
    inlines = [UserProfileInline]
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'strategy_count', 'is_staff', 'date_joined'
    ]
    
    def strategy_count(self, obj):
        """Count of user's strategies"""
        count = obj.strategy_set.count()
        if count > 0:
            url = reverse('admin:core_strategy_changelist') + f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{} strategies</a>', url, count)
        return "0 strategies"
    strategy_count.short_description = 'Strategies'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('strategy_set')