# Django imports
from django.db.models import Model, DateTimeField, CharField, ForeignKey,\
    UUIDField, CASCADE
# import custom models
from api.models.campaign import Campaign
from api.models.client import Client
# Python imports
from uuid import uuid4
from datetime import datetime
import pytz


class Message(Model):

    # start: obj was choosen for sending and tried to make request to API
    # done: API return 200
    # later: API return 400 and stop_time > now time

    STATUS_CHOISES = [
        ('start', 'start'),
        ('done', 'done'),
        ('later', 'later'),
        ('never', 'never')
    ]

    class Meta:
        db_table = 'messages'

    time_was_sended = DateTimeField(null=True)
    status = CharField(default='done', max_length=64, choices=STATUS_CHOISES)
    client_fk = ForeignKey(
        Client,
        related_name='client_messages',
        on_delete=CASCADE
    )
    campaign_fk = ForeignKey(
        Campaign,
        related_name='campaign_messages',
        on_delete=CASCADE
    )

    def message_done(self):

        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())

        self.time_was_sended = now
        self.status = 'done'
        self.save()

    def message_later(self):

        self.status = 'later'
        self.save()

    def message_never(self):

        self.status = 'never'
        self.save()
