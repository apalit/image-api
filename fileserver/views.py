import re
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import ImageUpload, Thumbnail
from fileserver.renderers import JPGRenderer, PNGRenderer


class ImageFileView(APIView):
    """
    This view provides the actual image content
    """
    permission_classes = (AllowAny,)  # noqa
    renderer_classes = (
        JPGRenderer,
        PNGRenderer,
    )

    def get(self, *args, **kwargs):
        object_type, image_path = self.parse_path()
        try:
            image = self.get_image(object_type, image_path)
        except ObjectDoesNotExist:
            raise NotFound
        extension = Path(image.name).suffix.replace('.', '')
        return Response(
            data=image, content_type=f'image/{extension}', status=status.HTTP_200_OK
        )

    def parse_path(self):
        path: str = self.request.path
        match = re.search(
            r'^/media/(imageupload|thumbnail|exp)/[0-9a-f]{32}/[0-9a-f]{32}\.(jpeg|jpg|png)$',  # noqa
            path,
        )
        if not match:
            raise ValidationError('The url format is not valid')

        path = path.replace('/media/', '')
        components = path.split('/', 1)
        object_type = components[0]
        return object_type, path

    def get_image(self, object_type, image_path):
        if object_type == 'exp':
            image = self.get_expiring_image(image_path)
        elif object_type == 'imageupload':
            image = self.get_base_image(image_path)
        else:
            image = self.get_thumbnail_image(image_path)
        return image

    def get_base_image(self, image_path):
        image_upload = ImageUpload.objects.get(image=image_path)
        return image_upload.image

    def get_thumbnail_image(self, image_path):
        thumbnail = Thumbnail.objects.get(thumbnail_image=image_path)
        return thumbnail.thumbnail_image

    def get_expiring_image(self, image_path):
        image_upload = ImageUpload.objects.get(
            image_expiry_links__expiry_date_time__gt=timezone.now(),
            image_expiry_links__link_alias=image_path,
        )
        return image_upload.image
