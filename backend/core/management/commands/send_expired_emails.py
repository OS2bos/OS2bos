from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Activity
from core.utils import send_activity_expired_email


class Command(BaseCommand):
    help = (
        "Sends emails for activities that have "
        "expired in the last number of days."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-l",
            "--last-days",
            default=1,
            type=int,
            help=(
                "Send expired emails for activities that are --last-days old."
            ),
        )

    def handle(self, *args, **options):
        last_days = options["last_days"]
        now_date = timezone.now().date()

        activities = Activity.objects.filter(
            end_date__gte=now_date - timedelta(days=last_days),
            end_date__lt=now_date,
            status=Activity.STATUS_GRANTED,
        )

        for activity in activities:
            if not activity.triggers_payment_email:
                return
            send_activity_expired_email(activity)
