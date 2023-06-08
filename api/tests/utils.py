from pathlib import Path
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO
import sys
from api.models import ImageUpload, ImageExpiringLink


def create_expiring_link(image_upload, expiry_in_seconds=300):
    expiring_link = ImageExpiringLink(
        base_image=image_upload,
        expiry_in_seconds=expiry_in_seconds,
        description=f'link expiring in {expiry_in_seconds} seconds'
    )
    expiring_link.save()
    return expiring_link


def create_image(user, size=(400, 400), file_name='test.png'):
    extension = Path(file_name).suffix
    if extension == '.png':
        model = 'RGBA'
        content_type = 'image/png'
    else:
        model = 'RGB'
        content_type = 'image/jpeg'
    # create image in memory
    mock_file = BytesIO()
    image = Image.new(model, size=size, color=(155, 0, 0))

    image.save(mock_file, extension.replace('.', ''))
    mock_file.name = file_name
    # create ImageUpload
    image_upload = ImageUpload(
        name='test image',
        user=user
    )
    image_upload.image = InMemoryUploadedFile(
        mock_file,
        'ImageField',
        file_name,
        content_type,
        sys.getsizeof(mock_file),
        None
    )
    image_upload.save()
    mock_file.seek(0)
    return image_upload
