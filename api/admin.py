# default import
from django.contrib import admin
# import models
from api.models.client import Client
from api.models.campaign import Campaign
from api.models.message import Message


class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number']


class CampaignAdmin(admin.ModelAdmin):
    list_display = ['id']


admin.site.register(Message)
admin.site.register(Client, ClientAdmin)
admin.site.register(Campaign, CampaignAdmin)
