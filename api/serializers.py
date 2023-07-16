# DRF imports
from rest_framework import serializers

# import models
from api.models.client import Client
from api.models.campaign import Campaign

# DRF imports
from rest_framework.serializers import ModelSerializer

# Python imports
import datetime
import pytz


class ClientSerializer(ModelSerializer):

    class Meta:
        model = Client
        fields = [
            'phone_number',
            'phone_city_code',
            'tag',
            'time_zone',
            'available_time_start',
            'available_time_finish'
        ]

    def validate(self, attrs):

        phone_number_code = attrs.get('phone_number')[1:4]
        city_code = attrs.get('phone_city_code')
        available_time_start = attrs.get('available_time_start')
        available_time_finish = attrs.get('available_time_finish')

        if phone_number_code != city_code:
            raise serializers.ValidationError(
                'city_code conflict with phone_number')

        if (available_time_start and not available_time_finish) or (available_time_finish and not available_time_start):
            raise serializers.ValidationError(
                'available_time_start and available_time_finish or null for both')

        return attrs


class CampaignSerializer(ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(read_only=True)
    campaign_messages = serializers.StringRelatedField(
        many=True, read_only=True
    )

    class Meta:
        model = Campaign
        fields = [
            'id',
            'campaign_messages',
            'time_to_send',
            'text',
            'client_filter',
            'stop_time'
        ]

    def validate(self, attrs):

        time_zone = pytz.UTC
        now = time_zone.localize(datetime.datetime.utcnow())

        time_to_send = attrs.get('time_to_send')
        stop_time = attrs.get('stop_time')

        if time_to_send >= stop_time:
            raise serializers.ValidationError('stop_time must be more than time_to_send')

        if stop_time < now:
            raise serializers.ValidationError('stop_time must be more than now')

        return attrs


class CampaignListSerializer(serializers.ModelSerializer):

    message_counter = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = ['id', 'message_counter', 'status']

    def get_message_counter(self, obj):
        return obj.get('message_count')

    def get_status(self, obj):
        return obj.get('campaign_messages__status')