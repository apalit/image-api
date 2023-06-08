from django.urls import re_path

from fileserver.views import ImageFileView


urlpatterns = [
    re_path('^(?P<path>.*)$', ImageFileView.as_view())
]
