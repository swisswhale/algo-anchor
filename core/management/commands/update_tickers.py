from django.core.management.base import BaseCommand
from core.models import Security
import yfinance as yf

class Command(BaseCommand):
    help = "Updates market cap and sector info for all securities"

    def handle(self, *args, **kwargs):
        for sec in Security.objects.all():
            try:
                info = yf.Ticker(sec.symbol).info
                sec.market_cap = info.get('marketCap')
                sec.sector = info.get('sector')
                sec.save()
                self.stdout.write(f"Updated {sec.symbol}")
            except Exception as e:
                self.stderr.write(f"Error updating {sec.symbol}: {e}")