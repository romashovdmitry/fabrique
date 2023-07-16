# DRF imports
from rest_framework.generics import CreateAPIView, UpdateAPIView,\
    DestroyAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# import models
from api.models.client import Client
from api.models.campaign import Campaign

# import serialazers
from api.serializers import ClientSerializer, CampaignSerializer, \
    CampaignListSerializer

# Django imports
from django.db.models import Count
from django.shortcuts import get_object_or_404

# Python imports
import datetime
import pytz

# import custom classes, functions
from message_sender.send_message import send_message_helper, celery_helper


def campaign_list_helper(queryset):
    data = {}
    for camp in queryset:
        camp_id = str(camp['id'])
        if camp_id not in data:
            data[camp_id] = []
        serializer = CampaignListSerializer(camp)
        data[camp_id].append(serializer.data)
    return data

class ClientViewSet(ModelViewSet):
    ''' to work with clients '''
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    http_method_names = ['post', 'put', 'delete']


class CampaignViewSet(ModelViewSet):
    ''' to work with Campaigns '''
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    http_method_names = ['post', 'get', 'delete', 'put']

    def list(self, request):
        ''' get list of all campaigns with message counting '''
        queryset = Campaign.objects.annotate(message_count=Count('campaign_messages__status')).values(
            'id', 'campaign_messages__status', 'message_count')
        data = campaign_list_helper(queryset)

        return Response(data)

    def retrieve(self, request, pk=None):

        campaign = get_object_or_404(self.queryset, pk=pk)
        return Response(
            CampaignSerializer(campaign).data
        )

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            campaign_obj = serializer.save()
            # resolving by pytz
            # TypeError: can't compare
            # offset-naive and offset-aware datetimes
            time_zone = pytz.UTC
            now = time_zone.localize(datetime.datetime.utcnow())
            if now >= campaign_obj.time_to_send:
                send_message_helper(campaign_obj)
            else:
                celery_helper.apply_async(args=[campaign_obj.id], eta=campaign_obj.time_to_send)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
