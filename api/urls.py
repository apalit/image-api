from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import ImageExpiringLinkView, ImageView

router = DefaultRouter()
router.register(r'images', ImageView, basename='image')
router.register(
    r'expiring-links', ImageExpiringLinkView, basename='expiring-link'
)

urlpatterns = [
    path('', include(router.urls))
]
