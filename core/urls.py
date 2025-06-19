from django.urls import path
from core.views import strategy_views
from .views import (
    dashboard_views,
    auth_views,
    profile_views,
    strategy_views,
)

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
    path('strategies/new/', strategy_views.strategy_create, name='strategy_create'), path('strategies/<int:pk>/', strategy_views.strategy_detail, name='strategy_detail'),
    path('strategies/<int:pk>/', strategy_views.strategy_detail, name='strategy_detail'),
    path('strategies/<int:pk>/edit/', strategy_views.strategy_edit, name='strategy_edit'),
    path('strategies/<int:pk>/rename/', strategy_views.strategy_rename, name='strategy_rename'),
    path('strategies/<int:pk>/delete/', strategy_views.strategy_delete, name='strategy_delete'),

    # Profile
    path('profile/', profile_views.profile_view, name='profile'),
    path('profile/edit/', profile_views.edit_profile, name='edit_profile'),
]