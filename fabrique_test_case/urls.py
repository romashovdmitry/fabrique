# default imports
from django.contrib import admin
from django.urls import path, include
from django.contrib.admin.views.decorators import staff_member_required

# Swagger imports
from fabrique_test_case.yasg import urlpatterns as SWAG

# import router, viewsets
from api.router import router

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Swagger URLS
urlpatterns += SWAG
# router URLS
urlpatterns += router.urls
