from django.conf import settings
from rest_framework import serializers

from api.models import ImageExpiringLink, ImageUpload, Thumbnail


class ThumbnailSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Thumbnail
        fields = ('id', 'height', 'thumbnail_url')
        read_only_fields = ('id', 'height', 'thumbnail_url')

    def get_thumbnail_url(self, obj):
        return f'{settings.MEDIA_BASE_URL}{obj.thumbnail_image.name}'


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
            'create_date_time',
            'thumbnails',
            'image_url',
            'status',
        )
        read_only_fields = (
            'id',
            'type',
            'create_date_time',
            'thumbnails',
            'image_url',
            'status',
        )

    def get_image_url(self, obj):
        # the image_url is retrievable only for users who can see original image
        include_image_link = self.context.get('include_original_image', False)
        if include_image_link:
            return f'{settings.MEDIA_BASE_URL}{obj.image.name}'
        else:
            return None


class ImageExpiringLinkSerializer(serializers.ModelSerializer):
    link_url = serializers.SerializerMethodField(required=False)

    class Meta:
        model = ImageExpiringLink
        fields = (
            'id',
            'description',
            'expiry_in_seconds',
            'create_date_time',
            'expiry_date_time',
            'base_image',
            'link_url',
        )
        read_only_fields = ('id', 'create_date_time', 'expiry_date_time', 'link_url')

    def get_link_url(self, obj):
        return f'{settings.MEDIA_BASE_URL}{obj.link_alias}'

    def validate_base_image(self, value):
        # the base_image should be owned by the user
        user = self.context['request'].user
        if value.user == user:
            return value
        else:
            raise serializers.ValidationError(
                'You do not have permissions to the image'
            )

    def validate_expiry_in_seconds(self, value):
        # the value should be between two values
        if settings.EXPIRY_MIN_VALUE <= value <= settings.EXPIRY_MAX_VALUE:
            return value
        else:
            raise serializers.ValidationError(
                'Expiry_in_seconds should be between '
                f'{settings.EXPIRY_MIN_VALUE} and {settings.EXPIRY_MAX_VALUE}'
            )
