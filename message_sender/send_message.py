# import Django packages
from celery import current_app
from celery import shared_task
from django.core.mail import send_mail

# import Models
from api.models.client import Client
from api.models.campaign import Campaign
from api.models.message import Message

# Python imports
from datetime import datetime, timedelta, time
import pytz
import requests
import json

# .env imports
import os
from dotenv import load_dotenv
load_dotenv()

# config-variables import
from fabrique_test_case.settings import EMAIL_HOST_USER, EMAIL_RECIPIENT


def create_message_object(client, campaign):

    if not Message.objects.filter(campaign_fk=campaign).filter(client_fk=client).exists():
        new_message = Message.objects.create(
            client_fk=client,
            campaign_fk=campaign,
            status='start'
        )
    else:
        new_message = Message.objects.get(campaign_fk=campaign, client_fk=client)
    message_obj = {
        'message': new_message,
        'id': new_message.id,
        'phone': client.phone_number,
        'text': campaign.text
    }
    return message_obj


@shared_task
def send_to_current_user_helper(camp_id, client_id):
    campaign = Campaign.objects.get(id=camp_id)
    client = Client.objects.get(id=client_id)
    message_obj = create_message_object(client, campaign)
    api_message([message_obj])


def start_message(campaign, relevant_clients):

    messages_to_send = []

    for client in relevant_clients:

        if not Message.objects.filter(client_fk=client).filter(campaign_fk=campaign).exists():

            # working with time zone of client
            time_zone = pytz.UTC
            now = time_zone.localize(datetime.utcnow())
            current_date = datetime.now().date()

            # can't save available_time_start without available_time_finish
            if client.available_time_start:

                # firstly, everything to UTC
                target_timezone = pytz.timezone(client.time_zone)

                time_start = time(
                    hour=client.available_time_start.hour,
                    minute=client.available_time_start.minute,
                    second=client.available_time_start.second
                )

                client_time_start = datetime.combine(current_date, time_start)
                client_time_start = target_timezone.localize(client_time_start)
                client_time_start_utc = client_time_start.astimezone(pytz.UTC)

                time_finish = time(
                    hour=client.available_time_finish.hour,
                    minute=client.available_time_finish.minute,
                    second=client.available_time_finish.second
                )

                client_time_finish = datetime.combine(
                    current_date, time_finish)
                client_time_finish = target_timezone.localize(
                    client_time_finish)
                client_time_finish_utc = client_time_finish.astimezone(
                    pytz.UTC)

                if now < client_time_start_utc:
                    send_to_current_user_helper.apply_async(
                        args=[campaign.id, client.id], eta=client_time_start_utc)
                    continue

                elif now > client_time_finish_utc:
                    time_for_task = client_time_finish_utc + timedelta(days=1)
                    send_to_current_user_helper.apply_async(
                        args=[campaign.id, client.id], eta=time_for_task)
                    continue

            message_obj = create_message_object(client, campaign)
            messages_to_send.append(message_obj)

    return messages_to_send


def api_message(messages):

    if messages:

        for message in messages:

            url = f"https://probe.fbrq.cloud/v1/send/{message['id']}"
            token = os.getenv('API_TOKEN')
            # token = 'WRONG TOKEN'
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            data = {
                'id': message['id'],
                'phone': message['phone'],
                'text': message['text']
            }
            try:
                response = requests.post(
                    url, headers=headers, data=json.dumps(data))
                if response.status_code == 200:
                    message['message'].message_done()
                else:
                    print(
                        f'Ошибка при выполнении запроса: {response.status_code} {response.text}')
                    message['message'].message_later()
                    send_mail(
                        subject="Error! Request status is not 200. ",
                        message=f'{response.text}',
                        from_email=EMAIL_HOST_USER,
                        recipient_list=[EMAIL_RECIPIENT],
                        fail_silently=False  # Set this to False so that you will be noticed in any exception raised
                    )
            except Exception as ex:
                message['message'].message_later()
                send_mail(
                    subject="Error! Error in request. ",
                    message=f'{ex}',
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[EMAIL_RECIPIENT],
                    fail_silently=False  # Set this to False so that you will be noticed in any exception raised
                )
        return 'processing messages finished'

    return 'no relevant messages'


def send_message_helper(campaign):

    relevant_clients = Client.get_relevant_clients(campaign)
    messages_to_send = start_message(campaign, relevant_clients)
    result = api_message(messages_to_send)
    return result


@shared_task
def celery_helper(camp_id):
    campaign = Campaign.objects.get(id=camp_id)
    send_message_helper(campaign)
