import os
import sys
from io import BytesIO

from celery import shared_task
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image

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

    base_image = image_upload.image
    (name, extension) = os.path.splitext(base_image.name)
    width = base_image.width
    if extension.lower() == '.png':
        content_type = 'image/png'
    else:
        content_type = 'image/jpeg'

    for height in thumbnail_heights:
        size = (width, height)
        with Image.open(base_image.open()) as im:
            im.thumbnail(size, Image.ANTIALIAS)
            output = BytesIO()
            im.save(output, format=im.format)

            thumbnail = Thumbnail(height=height, base_image=image_upload)
            thumbnail.thumbnail_image = InMemoryUploadedFile(
                output,
                'ImageField',
                f'{name}-thumb-{height}{extension}',
                content_type,
                sys.getsizeof(output),
                None,
            )
            thumbnail.save()
    # update status
    image_upload.status = 'Thumbnails created'
    image_upload.save()
