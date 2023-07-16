from rest_framework.routers import DefaultRouter

from api.views import ClientViewSet, CampaignViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='clients')
router.register(r'campaigns', CampaignViewSet, basename='campaigns')
