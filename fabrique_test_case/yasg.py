# django impoprts
from django.urls import re_path
from django.urls import path

# DRF imports
from rest_framework import permissions

# Swagger imports
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


description = 'This application enables to send process with clients, '\
    'messages and message-campaigns.'

schema_view = get_schema_view(
   openapi.Info(
      title="Test Case API",
      default_version='v1',
      description=description,
      terms_of_service=None,
      contact=openapi.Contact(email="romashov.dmitry.py@gmail.com")
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
   path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]
