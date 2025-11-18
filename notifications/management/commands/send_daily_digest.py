from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.services import NotificationScheduler

User = get_user_model()


class Command(BaseCommand):
    help = 'Send daily digest notifications to users who have opted in'

    def handle(self, *args, **options):
        """
        Send daily digest to all users with daily_digest enabled
        """
        self.stdout.write('Starting daily digest notification task...')

        users_with_digest = User.objects.filter(
            notification_preferences__daily_digest=True
        )

        count = 0
        for user in users_with_digest:
            try:
                NotificationScheduler.send_daily_digest(user)
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Sent digest to {user.username}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send digest to {user.username}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent {count} daily digest emails')
        )
