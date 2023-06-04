from django.urls import path
from api.views import ImageCreateListView, ImageDetailView


urlpatterns = [
    path('images', ImageCreateListView.as_view(), name='images'),
    path('images/<int:pk>', ImageDetailView.as_view(), name='image-detail')
]
