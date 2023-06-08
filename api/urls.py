from django.urls import include, path
from api.views import ImageView, ImageExpiringLinkView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'images', ImageView, basename='image')
router.register(
    r'expiring-links', ImageExpiringLinkView, basename='expiring-link'
)

urlpatterns = [
    path('', include(router.urls))
]
