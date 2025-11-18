# analytics/management/commands/generate_snapshots.py
"""
Django management command to generate analytics snapshots
Usage: python manage.py generate_snapshots [--date YYYY-MM-DD] [--period daily|weekly|monthly]
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
from analytics.services import AnalyticsEngine
from analytics.models import AnalyticsSnapshot


class Command(BaseCommand):
    help = 'Generate analytics snapshots for specified period and date'

    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            '--date',
            type=str,
            help='Date for snapshot (YYYY-MM-DD format). Defaults to today.',
        )
        parser.add_argument(
            '--period',
            type=str,
            choices=['daily', 'weekly', 'monthly', 'all'],
            default='daily',
            help='Period type for snapshot',
        )
        parser.add_argument(
            '--backfill',
            type=int,
            help='Backfill N days of snapshots',
        )

    def handle(self, *args, **options):
        """Execute the command"""
        # Parse date
        if options['date']:
            try:
                target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                raise CommandError('Invalid date format. Use YYYY-MM-DD.')
        else:
            target_date = timezone.now().date()

        period = options['period']
        backfill_days = options.get('backfill')

        # Handle backfill
        if backfill_days:
            self.stdout.write(
                self.style.WARNING(
                    f'Backfilling {backfill_days} days of snapshots...'
                )
            )
            self._backfill_snapshots(target_date, backfill_days)
            return

        # Generate snapshot(s) for specified period
        if period == 'all':
            self._generate_all_periods(target_date)
        elif period == 'daily':
            self._generate_daily(target_date)
        elif period == 'weekly':
            self._generate_weekly(target_date)
        elif period == 'monthly':
            self._generate_monthly(target_date)

    def _generate_daily(self, target_date):
        """Generate daily snapshot"""
        self.stdout.write(f'Generating daily snapshot for {target_date}...')

        try:
            snapshot = AnalyticsEngine.generate_daily_snapshot(target_date)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Daily snapshot created: {snapshot.total_predictions} predictions'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to create daily snapshot: {str(e)}')
            )

    def _generate_weekly(self, target_date):
        """Generate weekly snapshot"""
        self.stdout.write(f'Generating weekly snapshot for week ending {target_date}...')

        try:
            snapshot = AnalyticsEngine.generate_weekly_snapshot(target_date)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Weekly snapshot created: {snapshot.total_predictions} predictions'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to create weekly snapshot: {str(e)}')
            )

    def _generate_monthly(self, target_date):
        """Generate monthly snapshot"""
        self.stdout.write(f'Generating monthly snapshot for {target_date.strftime("%B %Y")}...')

        # Get first and last day of month
        first_day = target_date.replace(day=1)
        if target_date.month == 12:
            last_day = target_date.replace(day=31)
        else:
            last_day = target_date.replace(month=target_date.month + 1, day=1) - timedelta(days=1)

        try:
            from detection.models import Prediction
            from django.db.models import Count, Avg

            predictions = Prediction.objects.filter(
                created_at__date__range=[first_day, last_day]
            )

            snapshot, created = AnalyticsSnapshot.objects.update_or_create(
                period_type='monthly',
                snapshot_date=last_day,
                defaults={
                    'total_predictions': predictions.count(),
                    'covid_positive': predictions.filter(final_diagnosis='COVID').count(),
                    'normal_cases': predictions.filter(final_diagnosis='Normal').count(),
                    'viral_pneumonia': predictions.filter(final_diagnosis='Viral Pneumonia').count(),
                    'lung_opacity': predictions.filter(final_diagnosis='Lung Opacity').count(),
                    'avg_inference_time': predictions.aggregate(Avg('inference_time'))['inference_time__avg'],
                    'avg_confidence': predictions.aggregate(Avg('consensus_confidence'))['consensus_confidence__avg'],
                }
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Monthly snapshot created: {snapshot.total_predictions} predictions'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to create monthly snapshot: {str(e)}')
            )

    def _generate_all_periods(self, target_date):
        """Generate snapshots for all periods"""
        self.stdout.write(
            self.style.WARNING('Generating snapshots for all periods...')
        )
        self._generate_daily(target_date)
        self._generate_weekly(target_date)
        self._generate_monthly(target_date)

    def _backfill_snapshots(self, end_date, days):
        """Backfill snapshots for multiple days"""
        success_count = 0
        error_count = 0

        for i in range(days):
            target_date = end_date - timedelta(days=i)

            try:
                snapshot = AnalyticsEngine.generate_daily_snapshot(target_date)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {target_date}: {snapshot.total_predictions} predictions'
                    )
                )
                success_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ {target_date}: {str(e)}')
                )
                error_count += 1

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Backfill complete: {success_count} successful, {error_count} errors'
            )
        )
