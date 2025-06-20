from django.core.management.base import BaseCommand
from core.models import Security
import yfinance as yf
import time
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Updates market cap and sector info for all securities"

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbol',
            type=str,
            help='Update specific symbol only'
        )
        parser.add_argument(
            '--outdated-only',
            action='store_true',
            help='Only update securities older than 24 hours'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of securities to update'
        )

    def handle(self, *args, **options):
        symbol = options.get('symbol')
        outdated_only = options.get('outdated_only')
        limit = options.get('limit')

        if symbol:
            # Update specific symbol
            try:
                security = Security.objects.get(symbol=symbol.upper())
                self.update_security(security)
                self.stdout.write(
                    self.style.SUCCESS(f"Updated {security.symbol}")
                )
            except Security.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Security {symbol} not found")
                )
            return

        # Filter securities to update
        queryset = Security.objects.filter(is_active=True)
        
        if outdated_only:
            cutoff_time = timezone.now() - timedelta(hours=24)
            queryset = queryset.filter(last_updated__lt=cutoff_time)
        
        securities = queryset.order_by('last_updated')[:limit]
        
        if not securities:
            self.stdout.write("No securities to update")
            return

        self.stdout.write(f"Updating {len(securities)} securities...")
        
        updated_count = 0
        failed_count = 0

        for i, security in enumerate(securities, 1):
            try:
                self.stdout.write(f"Updating {security.symbol} ({i}/{len(securities)})...")
                self.update_security(security)
                updated_count += 1
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f"Error updating {security.symbol}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed! Updated: {updated_count}, Failed: {failed_count}"
            )
        )

    def update_security(self, security):
        """Update a single security with latest data from yfinance"""
        ticker = yf.Ticker(security.symbol)
        info = ticker.info
        
        # Update fields
        security.name = info.get('longName') or info.get('shortName') or security.name
        security.sector = info.get('sector') or security.sector
        security.industry = info.get('industry') or security.industry
        security.market_cap = info.get('marketCap') or security.market_cap
        security.currency = info.get('currency', 'USD')
        
        # Update exchange if available
        exchange = info.get('exchange', '').upper()
        if 'NYSE' in exchange:
            security.exchange = 'NYSE'
        elif 'NASDAQ' in exchange:
            security.exchange = 'NASDAQ'
        elif 'AMEX' in exchange:
            security.exchange = 'AMEX'
        
        security.save()  # This will trigger market cap category update