from celery import shared_task
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image
import os
import sys

from api.models import ImageUpload, Thumbnail


@shared_task
def create_thumbnails_task(image_upload_pk):
    image_upload: ImageUpload = ImageUpload.objects.get(pk=image_upload_pk)
    if not image_upload.image:
        return

    user = image_upload.user
    # get user plan
    plan = user.userplan.plan
    thumbnail_heights = plan.thumbnail_heights
    image_full_name = image_upload.image.name
    (name, extension) = os.path.splitext(image_full_name)

    if extension.lower() == '.png':
        content_type = 'image/png'
    else:
        content_type = 'image/jpeg'

    for height in thumbnail_heights:
        size = (height, height)
        with Image.open(image_upload.image.open()) as im:
            im.thumbnail(size, Image.ANTIALIAS)
            output = BytesIO()
            im.save(output, format=im.format)

            thumbnail = Thumbnail(
                user=user, height=height, base_image=image_upload
            )
            thumbnail.thumbnail_image = InMemoryUploadedFile(
                output,
                'ImageField',
                f'{name}-thumb-{height}{extension}',
                content_type,
                sys.getsizeof(output),
                None
            )
            thumbnail.save()
