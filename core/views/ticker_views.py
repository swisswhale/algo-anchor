from django.http import JsonResponse
from core.models import Security
import yfinance as yf

def tickers_by_asset_class(request):
    asset_class_id = request.GET.get('asset_class')
    results = []

    if asset_class_id:
        securities = Security.objects.filter(asset_class__id=asset_class_id)[:50]
        results = [{'symbol': s.symbol, 'name': s.name} for s in securities]

    return JsonResponse(results, safe=False)

def ticker_search(request):
    query = request.GET.get('q', '').strip().upper()
    results = []

    if query:
        try:
            ticker = yf.Ticker(query)
            info = ticker.info
            name = info.get('shortName') or info.get('longName') or ''
            if name:
                results.append({'symbol': query, 'name': name})
        except Exception:
            pass

    return JsonResponse(results, safe=False)