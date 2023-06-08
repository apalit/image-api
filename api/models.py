import uuid
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    name = models.CharField(max_length=256)
    thumbnail_heights = ArrayField(models.IntegerField())
    include_original_image = models.BooleanField(default=False)
    expiring_link = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserPlan(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='user_plans')


def user_directory_path(instance, filename):
    extension = Path(filename).suffix
    name = instance.__class__.__name__.lower()
    # file will be uploaded to MEDIA_ROOT/{name}/id/uniqueid/uniqueid.extension
    return f'{name}/{uuid.uuid4().hex}/{uuid.uuid4().hex}{extension}'


class ImageUpload(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=1024, null=True, blank=True)
    image = models.ImageField(
        upload_to=user_directory_path,
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg'))],
    )
    create_date_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=265, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        create = self._state.adding
        if create:
            # set status during create
            self.status = 'Processing thumbnails'
        super().save(*args, **kwargs)
        if create:
            # call create thumbnail task during create
            from api.tasks import create_thumbnails_task

            create_thumbnails_task.delay(self.pk)


class Thumbnail(models.Model):
    height = models.IntegerField()
    thumbnail_image = models.ImageField(
        upload_to=user_directory_path,
    )
    base_image = models.ForeignKey(
        ImageUpload, on_delete=models.CASCADE, related_name='thumbnails'
    )


class ImageExpiringLink(models.Model):
    base_image = models.ForeignKey(
        ImageUpload, on_delete=models.CASCADE, related_name='image_expiry_links'
    )
    description = models.CharField(max_length=1024, null=True, blank=True)
    create_date_time = models.DateTimeField(auto_now_add=True)
    expiry_in_seconds = models.IntegerField()
    expiry_date_time = models.DateTimeField()
    link_alias = models.CharField(max_length=1024)

    def save(self, *args, **kwargs):
        # set expiry date time
        self.expiry_date_time = timezone.now() + timedelta(
            seconds=self.expiry_in_seconds
        )
        # set image link alias as exp/{uuid1}/{uuid2.base image extension}
        image = self.base_image.image
        extension = Path(image.name).suffix
        self.link_alias = f'exp/{uuid.uuid4().hex}/{uuid.uuid4().hex}{extension}'
        super().save(*args, **kwargs)
