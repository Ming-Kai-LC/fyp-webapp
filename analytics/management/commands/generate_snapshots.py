"""
Management command to generate analytics snapshots
Usage: python manage.py generate_snapshots [--date YYYY-MM-DD]
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from analytics.services import AnalyticsEngine


class Command(BaseCommand):
    help = 'Generate analytics snapshots for the specified date or today'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date in YYYY-MM-DD format (default: today)',
        )

    def handle(self, *args, **options):
        date_str = options.get('date')

        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Invalid date format. Use YYYY-MM-DD')
                )
                return
        else:
            date = timezone.now().date()

        self.stdout.write(f'Generating analytics snapshot for {date}...')

        try:
            snapshot = AnalyticsEngine.generate_daily_snapshot(date=date)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created snapshot: {snapshot}'
                )
            )
            self.stdout.write(f'  - Total predictions: {snapshot.total_predictions}')
            self.stdout.write(f'  - COVID positive: {snapshot.covid_positive}')
            self.stdout.write(f'  - Normal cases: {snapshot.normal_cases}')
            self.stdout.write(f'  - Average confidence: {snapshot.avg_confidence}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating snapshot: {str(e)}')
            )
