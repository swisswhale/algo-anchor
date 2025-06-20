from django.urls import path
from core.views import dashboard_views, auth_views, profile_views, strategy_views, ticker_views, backtest_views

urlpatterns = [
    # Public home
    path('', dashboard_views.home, name='home'),

    # Auth
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('register/', auth_views.register_view, name='register'),

    # Dashboard
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),

    # Strategies
    path('strategies/', strategy_views.strategy_list, name='strategy_list'),
    path('strategies/new/', strategy_views.strategy_create, name='strategy_create'), 
    path('strategies/<int:pk>/', strategy_views.strategy_detail, name='strategy_detail'),
    path('strategies/<int:pk>/edit/', strategy_views.strategy_edit, name='strategy_edit'),
    path('strategies/<int:pk>/rename/', strategy_views.strategy_rename, name='strategy_rename'),
    path('strategies/<int:pk>/delete/', strategy_views.strategy_delete, name='strategy_delete'),

    # Backtest URLs
    path('strategies/<int:strategy_id>/backtest/', backtest_views.backtest_detail, name='backtest_detail'),
    path('strategies/<int:strategy_id>/backtest/rerun/', backtest_views.rerun_backtest, name='rerun_backtest'),
    path('strategies/<int:strategy_id>/backtest/api/', backtest_views.backtest_api, name='backtest_api'),
    path('backtests/compare/', backtest_views.compare_strategies, name='compare_strategies'),

    # Profile
    path('profile/', profile_views.profile_view, name='profile'),
    path('profile/edit/', profile_views.edit_profile, name='edit_profile'),
    path('profile/change-password/', profile_views.change_password, name='change_password'),
    
    # Ticker API endpoints
    path('api/ticker-search/', ticker_views.ticker_search, name='ticker_search'),
    path('api/ticker-autocomplete/', ticker_views.ticker_autocomplete, name='ticker_autocomplete'),
    path('api/ticker-validate/', ticker_views.ticker_validate, name='ticker_validate'),
    path('api/ticker/<str:symbol>/', ticker_views.ticker_info, name='ticker_info'),
    path('api/tickers/by-sector/', ticker_views.tickers_by_sector, name='tickers_by_sector'),
    path('api/tickers/by-market-cap/', ticker_views.tickers_by_market_cap, name='tickers_by_market_cap'),
    path('api/sectors/', ticker_views.sectors_list, name='sectors_list'),
    path('api/tickers/', ticker_views.tickers_by_asset_class, name='tickers_by_asset_class'),  # Legacy
]