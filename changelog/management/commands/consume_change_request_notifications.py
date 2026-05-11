from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from changelog.rabbitmq import consume_status_changes


class Command(BaseCommand):
    help = 'Consumes change request status updates and sends email notifications.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Waiting for change request updates...'))

        def _send_email(payload):
            subject = (
                f"Change request #{payload['request_number']} status updated"
            )
            previous_label = payload.get('previous_status_label', payload.get('previous_status'))
            current_label = payload.get('current_status_label', payload.get('current_status'))
            message = (
                f"Request: {payload.get('subject')}\n"
                f"Previous status: {previous_label}\n"
                f"Current status: {current_label}\n"
                f"Changed at: {payload.get('changed_at')}\n"
            )
            recipient = payload.get('email')
            if not recipient:
                self.stdout.write(self.style.WARNING('No recipient email in payload.'))
                return

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"Email sent to {recipient}"))

        consume_status_changes(_send_email)
