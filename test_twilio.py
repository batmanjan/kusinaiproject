from django.core.management.base import BaseCommand
from twilio.rest import Client
from django.conf import settings

class Command(BaseCommand):
    help = 'Test Twilio credentials'

    def handle(self, *args, **kwargs):
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        try:
            message = client.messages.create(
                body='Testing Twilio credentials',
                from_='+16467832567',  # Replace with your Twilio number
                to='+639760483137'      # Replace with a valid recipient number
            )
            self.stdout.write(self.style.SUCCESS(f"Message SID: {message.sid}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Twilio exception: {e}"))
            if e.response:
                self.stdout.write(self.style.ERROR(f"Exception details: {e.response}"))
