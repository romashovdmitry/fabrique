# Django imports
import pytz
from datetime import timedelta
from datetime import datetime
from api.models.message import Message
from django.core.mail import send_mail
from django.core.management import BaseCommand

from message_sender.send_message import celery_helper, create_message_object, api_message


class Command(BaseCommand):

    def handle(self, *args, **options):

        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())

        messages = Message.objects.filter(status='later').all()
        for message in messages:
            if now >= message.campaign_fk.time_to_send:
                message_obj = create_message_object(
                    client=message.client_fk,
                    campaign=message.campaign_fk
                )
                api_message([message_obj])
            elif message.campaign_fk.time_to_send < now:
                message.message_never()
            else:
                celery_helper.apply_async(args=[message.campaign_fk.id], eta=message.campaign_fk.time_to_send)
