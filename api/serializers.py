from django.conf import settings
from rest_framework import serializers

from api.models import ImageUpload, Thumbnail


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ('id', 'height', 'thumbnail_image')
        read_only_fields = ('id', 'height', 'thumbnail_image')


class ImageSerializer(serializers.ModelSerializer):
    thumbnails = ThumbnailSerializer(many=True, read_only=True)
    image = serializers.ImageField(write_only=True)
    image_url = serializers.SerializerMethodField(required=False)

    class Meta:
        model = ImageUpload
        fields = (
            'id',
            'name',
            'description',
            'image',
            'expiry',
            'create_date_time',
            'thumbnails',
            'image_url'
        )
        read_only_fields = (
            'id', 'type', 'create_date_time', 'thumbnails', 'image_url'
        )

    def get_image_url(self, obj):
        # the image_url is retrievable only for users who can see original image
        include_image_link = self.context.get('include_original_image', False)
        if include_image_link:
            return obj.image.url
        else:
            return None

    def validate_expiry(self, value):
        if value:
            # this can only be set if user has permission to do so.
            expiring_link = self.context.get('expiring_link', False)
            if not expiring_link:
                raise serializers.ValidationError(
                    'You do not have permission to set expiry'
                )
            # the value should be between two values
            if settings.EXPIRY_MIN_VALUE <= value <= settings.EXPIRY_MAX_VALUE:
                return value
            else:
                raise serializers.ValidationError(
                    f'Expiry should be between {settings.EXPIRY_MIN_VALUE} and'
                    f' {settings.EXPIRY_MAX_VALUE}'
                )
