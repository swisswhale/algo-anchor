"""
Management command to run backtests for strategies
Usage: python manage.py run_backtests [--strategy-id ID] [--force]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import Strategy, BacktestResult
from core.services.backtest_engine import run_comprehensive_backtest
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run backtests for strategies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--strategy-id',
            type=int,
            help='Run backtest for specific strategy ID'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-run backtest even if results exist'
        )
        parser.add_argument(
            '--user',
            help='Run backtests for strategies owned by specific user'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting backtest execution...')
        )

        try:
            # Filter strategies
            strategies = Strategy.objects.all()
            
            if options['strategy_id']:
                strategies = strategies.filter(id=options['strategy_id'])
            
            if options['user']:
                strategies = strategies.filter(user__username=options['user'])
            
            # Filter out strategies that already have results unless forced
            if not options['force']:
                strategies = strategies.filter(backtestresult__isnull=True)
            
            total_strategies = strategies.count()
            
            if total_strategies == 0:
                self.stdout.write(
                    self.style.WARNING('No strategies found to backtest.')
                )
                return
            
            self.stdout.write(
                f'Found {total_strategies} strategies to backtest.'
            )
            
            successful = 0
            failed = 0
            
            for strategy in strategies:
                try:
                    self.stdout.write(f'Running backtest for: {strategy.name}')
                    
                    # Delete existing results if forcing
                    if options['force']:
                        BacktestResult.objects.filter(strategy=strategy).delete()
                    
                    # Run backtest
                    with transaction.atomic():
                        results = run_comprehensive_backtest(strategy)
                        
                        if not results:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'No results generated for {strategy.name}'
                                )
                            )
                            failed += 1
                            continue
                        
                        # Create BacktestResult
                        backtest_result = BacktestResult.objects.create(
                            strategy=strategy,
                            cumulative_return=results.get('cumulative_return'),
                            annualized_return=results.get('annualized_return'),
                            sharpe_ratio=results.get('sharpe_ratio'),
                            sortino_ratio=results.get('sortino_ratio'),
                            win_rate=results.get('win_rate'),
                            max_drawdown=results.get('max_drawdown'),
                            volatility=results.get('volatility'),
                            total_trades=results.get('total_trades', 0),
                            winning_trades=results.get('winning_trades', 0),
                            losing_trades=results.get('losing_trades', 0),
                            avg_trade_return=results.get('avg_trade_return'),
                            avg_winning_trade=results.get('avg_winning_trade'),
                            avg_losing_trade=results.get('avg_losing_trade'),
                            value_at_risk_95=results.get('value_at_risk_95'),
                            calmar_ratio=results.get('calmar_ratio'),
                            benchmark_return=results.get('benchmark_return'),
                            alpha=results.get('alpha'),
                            beta=results.get('beta'),
                            backtest_start_date=results.get('backtest_start_date'),
                            backtest_end_date=results.get('backtest_end_date')
                        )
                        
                        # Create trade logs
                        from core.models import TradeLog
                        trade_log = results.get('trade_log', [])
                        for trade in trade_log:
                            TradeLog.objects.create(
                                backtest_result=backtest_result,
                                security=trade['security'],
                                trade_type=trade['type'],
                                date=trade['date'],
                                price=trade['price'],
                                quantity=trade['quantity'],
                                commission=trade['commission'],
                                signal_value=trade.get('signal_value'),
                                notes=f"Generated by management command"
                            )
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ {strategy.name}: '
                                f'Return: {results.get("cumulative_return", 0):.2%}, '
                                f'Sharpe: {results.get("sharpe_ratio", 0):.2f}, '
                                f'Trades: {results.get("total_trades", 0)}'
                            )
                        )
                        successful += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Failed to backtest {strategy.name}: {str(e)}'
                        )
                    )
                    failed += 1
                    logger.error(f'Backtest failed for {strategy.name}: {str(e)}')
            
            # Summary
            self.stdout.write('\n' + '='*50)
            self.stdout.write(f'Backtest Summary:')
            self.stdout.write(f'✓ Successful: {successful}')
            self.stdout.write(f'✗ Failed: {failed}')
            self.stdout.write(f'Total: {total_strategies}')
            
            if successful > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nSuccessfully completed {successful} backtests!'
                    )
                )
            
        except Exception as e:
            raise CommandError(f'Error running backtests: {str(e)}')
