# django imports
from django.db.models import Model, DateTimeField, TextField, JSONField,\
    UUIDField
from django.core.exceptions import ValidationError
# Python imports
from uuid import uuid4
import json
# import custom classes
from api.models.client import Client
# Python imports
from datetime import datetime
import pytz
import re


def validate_filter(value):
    ''' handle errors if there are '''
    try:

        if not isinstance(value, dict):
            raise ValidationError('Invalid JSON format. Expected an object.')

        if 'city_code' not in value.keys() or 'tag' not in value.keys():
            raise ValidationError(
                'Missing required keys "city_code" or "tag".')

        if value['tag'] not in Client.tags_for_validation:
            raise ValidationError(f'Wrong tag. Use on of this: '
                                  f'{Client.tags_for_validation}')

        if not bool(re.match(r"\d{3}$", value['city_code'])):
            raise ValidationError('city code must contain 3 digits')

    except (json.JSONDecodeError, TypeError):
        raise ValidationError('Invalid JSON format.')


class Campaign(Model):
    ''' Campaign model: id, text, client filter, start and stop time '''
    class Meta:
        db_table = 'campaigns'

    id = UUIDField(default=uuid4, primary_key=True)
    time_to_send = DateTimeField(null=True)
    text = TextField(null=True)
    client_filter = JSONField(null=True, validators=[validate_filter])
    stop_time = DateTimeField(null=True)
