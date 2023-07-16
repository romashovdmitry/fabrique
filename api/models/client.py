# Django imports
from django.db.models import Model, CharField, UUIDField, TimeField
from django.core.validators import MaxLengthValidator, MinLengthValidator,\
    RegexValidator
from django.core.exceptions import ValidationError

# Python imports
from uuid import uuid4
import datetime
import pytz


class Client(Model):
    ''' Client model: tags, phone_number, phone_city_code '''

    # just for example A, B, C
    tags_for_validation = ['A', 'B', 'C']
    # sorted because of without sorting, different order
    # create new migrations each docker compose up
    PYTZ_TIMEZONES = sorted([(f"{tz}", f"{tz}") for tz in pytz.all_timezones_set])
    TAGS = [
        ("A", "A"),
        ('B', 'B'),
        ('C', 'C')
    ]

    class Meta:
        db_table = 'clients'

    id = UUIDField(default=uuid4, primary_key=True)
    phone_number = CharField(
        max_length=11,
        null=True,
        unique=True,
        validators=[
            MaxLengthValidator(11),
            MinLengthValidator(11),
            RegexValidator(
                r'^7\d{10}$',
                'Введите номер телефона в формате 7XXXXXXXXXX'
            )
        ]
    )
    phone_city_code = CharField(max_length=3, null=True, validators=[
        MaxLengthValidator(3),
        MinLengthValidator(3),
        RegexValidator(
            r'^\d{3}$',
            'Введите код города в формате XXX'
        )
    ])
    tag = CharField(max_length=256, null=True, choices=TAGS)
    # there is no TimeZoneField in Django 4.1 that I use
    time_zone = CharField(max_length=64, null=True,
                          choices=PYTZ_TIMEZONES, default='etc/UTC')
    available_time_start = TimeField(null=True, blank=True)
    available_time_finish = TimeField(null=True, blank=True)

    @classmethod
    def get_relevant_clients(cls, campaign):

        relevant_clients = Client.objects.filter(tag=campaign.client_filter['tag']
                                                 ).filter(phone_city_code=campaign.client_filter['city_code']
                                                          ).all()

        return relevant_clients
