from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from core.models import Security
import yfinance as yf
import json

def tickers_by_sector(request):
    """Get tickers filtered by sector"""
    sector = request.GET.get('sector', '').strip()
    limit = int(request.GET.get('limit', 50))
    
    securities = Security.objects.filter(is_active=True)
    
    if sector:
        securities = securities.filter(sector__icontains=sector)
    
    securities = securities.select_related().order_by('symbol')[:limit]
    
    results = []
    for security in securities:
        results.append({
            'symbol': security.symbol,
            'name': security.name,
            'sector': security.sector,
            'market_cap': security.get_market_cap_display_value(),
            'exchange': security.get_exchange_display(),
        })
    
    return JsonResponse(results, safe=False)

def tickers_by_market_cap(request):
    """Get tickers filtered by market cap category"""
    market_cap_category = request.GET.get('category', '').upper()
    limit = int(request.GET.get('limit', 50))
    
    securities = Security.objects.filter(is_active=True)
    
    if market_cap_category in ['LARGE', 'MID', 'SMALL']:
        securities = securities.filter(market_cap_category=market_cap_category)
    
    securities = securities.select_related().order_by('-market_cap')[:limit]
    
    results = []
    for security in securities:
        results.append({
            'symbol': security.symbol,
            'name': security.name,
            'sector': security.sector,
            'market_cap': security.get_market_cap_display_value(),
            'market_cap_category': security.get_market_cap_category_display(),
        })
    
    return JsonResponse(results, safe=False)

def ticker_search(request):
    """Advanced ticker search with multiple criteria"""
    query = request.GET.get('q', '').strip()
    sector_filter = request.GET.get('sector', '').strip()
    market_cap_filter = request.GET.get('market_cap', '').strip()
    limit = int(request.GET.get('limit', 20))
    
    if not query:
        return JsonResponse([], safe=False)
    
    # Build search query
    search_query = Q()
    
    # Search by symbol or name
    search_query |= Q(symbol__icontains=query)
    search_query |= Q(name__icontains=query)
    
    # Apply filters
    securities = Security.objects.filter(search_query, is_active=True)
    
    if sector_filter:
        securities = securities.filter(sector__icontains=sector_filter)
    
    if market_cap_filter in ['LARGE', 'MID', 'SMALL']:
        securities = securities.filter(market_cap_category=market_cap_filter)
    
    securities = securities.order_by('symbol')[:limit]
    
    results = []
    for security in securities:
        results.append({
            'symbol': security.symbol,
            'name': security.name,
            'sector': security.sector,
            'market_cap': security.get_market_cap_display_value(),
            'exchange': security.get_exchange_display(),
        })
    
    return JsonResponse(results, safe=False)

def ticker_autocomplete(request):
    """Simple autocomplete for ticker symbols"""
    query = request.GET.get('q', '').strip().upper()
    limit = int(request.GET.get('limit', 10))
    
    if len(query) < 1:
        return JsonResponse([], safe=False)
    
    securities = Security.objects.filter(
        symbol__istartswith=query,
        is_active=True
    ).order_by('symbol')[:limit]
    
    results = []
    for security in securities:
        results.append({
            'symbol': security.symbol,
            'name': security.name,
            'label': f"{security.symbol} - {security.name}" if security.name else security.symbol,
            'value': security.symbol,
        })
    
    return JsonResponse(results, safe=False)

def ticker_info(request, symbol):
    """Get detailed information about a specific ticker"""
    try:
        security = Security.objects.get(symbol=symbol.upper(), is_active=True)
        
        data = {
            'symbol': security.symbol,
            'name': security.name,
            'sector': security.sector,
            'industry': security.industry,
            'market_cap': security.get_market_cap_display_value(),
            'market_cap_category': security.get_market_cap_category_display(),
            'exchange': security.get_exchange_display(),
            'currency': security.currency,
            'last_updated': security.last_updated.isoformat() if security.last_updated else None,
        }
        
        return JsonResponse(data)
        
    except Security.DoesNotExist:
        return JsonResponse({'error': 'Security not found'}, status=404)

def ticker_validate(request):
    """Validate a ticker symbol using yfinance"""
    symbol = request.GET.get('symbol', '').strip().upper()
    
    if not symbol:
        return JsonResponse({'error': 'Symbol required'}, status=400)
    
    try:
        # Check if we have it in our database first
        try:
            security = Security.objects.get(symbol=symbol, is_active=True)
            return JsonResponse({
                'valid': True,
                'source': 'database',
                'symbol': security.symbol,
                'name': security.name,
                'sector': security.sector,
            })
        except Security.DoesNotExist:
            pass
        
        # Validate with yfinance
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if info.get('symbol') or info.get('shortName') or info.get('longName'):
            return JsonResponse({
                'valid': True,
                'source': 'yfinance',
                'symbol': symbol,
                'name': info.get('longName') or info.get('shortName', ''),
                'sector': info.get('sector', ''),
            })
        else:
            return JsonResponse({'valid': False, 'error': 'Invalid ticker symbol'})
            
    except Exception as e:
        return JsonResponse({'valid': False, 'error': str(e)})

def sectors_list(request):
    """Get list of available sectors"""
    sectors = Security.objects.filter(
        is_active=True,
        sector__isnull=False
    ).exclude(sector='').values_list('sector', flat=True).distinct().order_by('sector')
    
    return JsonResponse(list(sectors), safe=False)

# Legacy function for backwards compatibility
def tickers_by_asset_class(request):
    """Legacy function - redirects to sector-based filtering"""
    return tickers_by_sector(request)