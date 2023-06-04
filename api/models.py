import uuid
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Plan(models.Model):
    name = models.CharField(max_length=256)
    thumbnail_heights = ArrayField(models.IntegerField())
    include_original_image = models.BooleanField(default=False)
    expiring_link = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserPlan(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name='user_plans'
    )


def user_directory_path(instance, filename):
    unique_id = uuid.uuid4().hex

    # file will be uploaded to MEDIA_ROOT/userid/uniqueid/<filename>
    return f'{instance.user.username}/{unique_id}/{filename}'


class ImageUpload(models.Model):

    name = models.CharField(max_length=256)
    description = models.CharField(max_length=1024, null=True, blank=True)
    image = models.ImageField(
        upload_to=user_directory_path,
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg'))]
    )
    expiry = models.IntegerField(null=True, blank=True)
    create_date_time = models.DateTimeField(auto_now_add=True)
    expiry_date_time = models.DateTimeField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.expiry:
            # set expiry datetime
            self.expiry_date_time = timezone.now() + timedelta(
                seconds=self.expiry
            )
        super().save(*args, **kwargs)
        # call create thumbnail task
        from api.tasks import create_thumbnails_task
        create_thumbnails_task.delay(self.pk)


class Thumbnail(models.Model):
    height = models.IntegerField()
    thumbnail_image = models.ImageField(upload_to=user_directory_path,)
    base_image = models.ForeignKey(
        ImageUpload,
        on_delete=models.CASCADE,
        related_name='thumbnails'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
