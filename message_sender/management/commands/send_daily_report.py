# Django imports
import pytz
from datetime import timedelta
from datetime import datetime
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.db.models import Count
from django.template import loader

# config-variables import
from fabrique_test_case.settings import EMAIL_HOST_USER, EMAIL_RECIPIENT

# import models
from api.models.message import Message, Campaign

# import custom DRF serializers, functions, etc.
from api.serializers import CampaignListSerializer
from api.views import campaign_list_helper


class FilterHelper:

    time_zone = pytz.UTC
    now = time_zone.localize(datetime.utcnow())
    yesterday = now - timedelta(days=3)
    yesterday_start = time_zone.localize(datetime(
        year=yesterday.year,
        month=yesterday.month,
        day=yesterday.day,
        hour=0,
        minute=0,
        second=0
    ))
    yesterday_finish = yesterday_start + timedelta(days=1)
    # for test on local
    yesterday_finish = now

    def filter_helper(self, status):

        return len(
            Message.objects.filter(time_was_sended__gte=FilterHelper.yesterday_start
                                   ).filter(time_was_sended__lte=FilterHelper.yesterday_finish
                                            ).filter(status=status
                                                     ).all()
        )


class Command(BaseCommand):

    def handle(self, *args, **options):

        # objects for subsequent processes 
        text_status_dict = {
            'done': 'Messages send, done by campaign: ',
            'start': 'Messages started by campaign: ',
            'later': 'Messages would be send later: ',
            'never': 'Messages never would be sended: '
        }

        detailed_text_header = 'More detailed about every campaign:\n\n'
        detailed_text = ''

        filter_helper = FilterHelper()

        # start process: stat on number of messages group by status, 
        # no matter campaign
        start_messages_mount = filter_helper.filter_helper('start')
        done_messages_mount = filter_helper.filter_helper('done')
        later_messages_mount = filter_helper.filter_helper('later')
        never_messages_mount = filter_helper.filter_helper('never')

        text_sum_start_messages = f'Messages in status "start": {start_messages_mount}\n'
        text_sum_done_messages = f'Messages are sent today: {done_messages_mount}\n'
        text_sum_later_messages = f'Messages are delayed for sending later: {later_messages_mount}\n'
        text_sum_never_messages = f'Messages never would be sended: {never_messages_mount}\n\n'

        # start process: stat on of messages group by status
        # for every certain compaign
        queryset = Campaign.objects.annotate(message_count=Count('campaign_messages__status')).values(
            'id', 'campaign_messages__status', 'message_count')
        data = campaign_list_helper(queryset)

        for key in data:
            detailed_text = f'Campaign ID: {str(key)} \n'
            for camp in data[key]:
                detailed_text += text_status_dict[camp['status']]
                detailed_text += str(camp['message_counter']) + '\n'

        email_text = text_sum_start_messages +\
            text_sum_done_messages +\
            text_sum_later_messages +\
            text_sum_never_messages +\
            detailed_text_header +\
            detailed_text
        
        send_mail(
            subject="Daily Report About Message Campaigns",
            message=f'{email_text}',
            from_email=EMAIL_HOST_USER,
            recipient_list=[EMAIL_RECIPIENT],
            fail_silently=False
        )