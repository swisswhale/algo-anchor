from django.core.management.base import BaseCommand
from core.models import Security
import yfinance as yf
from django.db.models import Q
from collections import Counter

class Command(BaseCommand):
    help = "Manage ticker database - cleanup, validate, and generate reports"

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['cleanup', 'validate', 'report', 'deactivate-invalid'],
            default='report',
            help='Action to perform'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        action = options['action']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        if action == 'cleanup':
            self.cleanup_duplicates(dry_run)
        elif action == 'validate':
            self.validate_tickers(dry_run)
        elif action == 'report':
            self.generate_report()
        elif action == 'deactivate-invalid':
            self.deactivate_invalid_tickers(dry_run)

    def cleanup_duplicates(self, dry_run=False):
        """Remove duplicate securities (keep the first one)"""
        self.stdout.write("Checking for duplicate securities...")
        
        seen_symbols = set()
        duplicates = []
        
        for security in Security.objects.order_by('created_at'):
            if security.symbol in seen_symbols:
                duplicates.append(security)
            else:
                seen_symbols.add(security.symbol)
        
        if duplicates:
            self.stdout.write(f"Found {len(duplicates)} duplicate securities:")
            for dup in duplicates:
                self.stdout.write(f"  - {dup.symbol} (ID: {dup.id})")
            
            if not dry_run:
                deleted_count = len(duplicates)
                for dup in duplicates:
                    dup.delete()
                self.stdout.write(
                    self.style.SUCCESS(f"Deleted {deleted_count} duplicate securities")
                )
        else:
            self.stdout.write("No duplicates found")

    def validate_tickers(self, dry_run=False):
        """Validate ticker symbols by checking with yfinance"""
        self.stdout.write("Validating ticker symbols...")
        
        invalid_tickers = []
        valid_tickers = []
        
        for security in Security.objects.filter(is_active=True):
            try:
                ticker = yf.Ticker(security.symbol)
                info = ticker.info
                
                # Check if ticker has basic info
                if info.get('symbol') or info.get('shortName') or info.get('longName'):
                    valid_tickers.append(security)
                else:
                    invalid_tickers.append(security)
                    
            except Exception:
                invalid_tickers.append(security)
        
        self.stdout.write(f"Valid tickers: {len(valid_tickers)}")
        self.stdout.write(f"Invalid tickers: {len(invalid_tickers)}")
        
        if invalid_tickers:
            self.stdout.write("Invalid tickers found:")
            for ticker in invalid_tickers:
                self.stdout.write(f"  - {ticker.symbol}")

    def deactivate_invalid_tickers(self, dry_run=False):
        """Deactivate invalid ticker symbols"""
        self.stdout.write("Deactivating invalid ticker symbols...")
        
        invalid_count = 0
        
        for security in Security.objects.filter(is_active=True):
            try:
                ticker = yf.Ticker(security.symbol)
                info = ticker.info
                
                # Check if ticker has basic info
                if not (info.get('symbol') or info.get('shortName') or info.get('longName')):
                    self.stdout.write(f"Deactivating {security.symbol}")
                    if not dry_run:
                        security.is_active = False
                        security.save()
                    invalid_count += 1
                    
            except Exception:
                self.stdout.write(f"Deactivating {security.symbol} (exception)")
                if not dry_run:
                    security.is_active = False
                    security.save()
                invalid_count += 1
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"Deactivated {invalid_count} invalid tickers")
            )

    def generate_report(self):
        """Generate a comprehensive report about the ticker database"""
        total_securities = Security.objects.count()
        active_securities = Security.objects.filter(is_active=True).count()
        inactive_securities = total_securities - active_securities
        
        # Count by sector
        sectors = Security.objects.filter(
            is_active=True, 
            sector__isnull=False
        ).exclude(sector='').values_list('sector', flat=True)
        sector_counts = Counter(sectors)
        
        # Count by exchange
        exchanges = Security.objects.filter(is_active=True).values_list('exchange', flat=True)
        exchange_counts = Counter(exchanges)
        
        # Count by market cap category
        market_caps = Security.objects.filter(is_active=True).values_list('market_cap_category', flat=True)
        market_cap_counts = Counter(market_caps)
        
        # Securities without complete data
        missing_name = Security.objects.filter(is_active=True, name='').count()
        missing_sector = Security.objects.filter(
            is_active=True
        ).filter(Q(sector__isnull=True) | Q(sector='')).count()
        missing_market_cap = Security.objects.filter(
            is_active=True, market_cap__isnull=True
        ).count()
        
        # Generate report
        self.stdout.write(self.style.SUCCESS("=== TICKER DATABASE REPORT ==="))
        self.stdout.write(f"Total Securities: {total_securities}")
        self.stdout.write(f"Active Securities: {active_securities}")
        self.stdout.write(f"Inactive Securities: {inactive_securities}")
        
        self.stdout.write("\n--- Top Sectors ---")
        for sector, count in sector_counts.most_common(10):
            self.stdout.write(f"{sector}: {count}")
        
        self.stdout.write("\n--- Exchanges ---")
        for exchange, count in exchange_counts.items():
            self.stdout.write(f"{exchange}: {count}")
        
        self.stdout.write("\n--- Market Cap Categories ---")
        for cap_category, count in market_cap_counts.items():
            self.stdout.write(f"{cap_category}: {count}")
        
        self.stdout.write("\n--- Data Completeness ---")
        self.stdout.write(f"Missing Name: {missing_name}")
        self.stdout.write(f"Missing Sector: {missing_sector}")
        self.stdout.write(f"Missing Market Cap: {missing_market_cap}")
        
        # Recent additions
        from django.utils import timezone
        from datetime import timedelta
        
        recent_cutoff = timezone.now() - timedelta(days=7)
        recent_additions = Security.objects.filter(created_at__gte=recent_cutoff).count()
        
        self.stdout.write(f"\nRecent Additions (7 days): {recent_additions}")
