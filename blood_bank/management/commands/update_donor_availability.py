from django.core.management.base import BaseCommand
from users.models import CustomUser
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Updates donor availability based on last donation date.'

    def handle(self, *args, **kwargs):
        ninety_days_ago = timezone.now().date() - datetime.timedelta(days=90)

        # Find users whose last donation was more than 90 days ago and are not available
        # Set them to available
        available_donors = CustomUser.objects.filter(
            last_donation_date__isnull=False,
            last_donation_date__lte=ninety_days_ago,
            is_available=False
        )
        updated_available_count = available_donors.update(is_available=True)

        # Find users whose last donation was less than 90 days ago and are available
        # Set them to not available
        unavailable_donors = CustomUser.objects.filter(
            last_donation_date__isnull=False,
            last_donation_date__gt=ninety_days_ago,
            is_available=True
        )
        updated_unavailable_count = unavailable_donors.update(is_available=False)

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_available_count} donors to available.'))
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_unavailable_count} donors to unavailable.')) 