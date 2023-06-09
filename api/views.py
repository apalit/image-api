from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.models import ImageExpiringLink, ImageUpload
from api.pagination import ImageCursorPagination
from api.permissions import HasExpiringLinkPermissions, HasPlan
from api.serializers import ImageExpiringLinkSerializer, ImageSerializer


class ImageView(GenericViewSet, CreateModelMixin, ListModelMixin, RetrieveModelMixin):
    """
    This view presents a list of all images uploaded by a user in paginated format
    and allows user to upload a new image. User should be logged in to access it.
    They can also view the details of a particular image created by them.
    """
    parser_classes = (
        MultiPartParser,
        FormParser,
    )
    permission_classes = (
        IsAuthenticated,
        HasPlan,
    )
    serializer_class = ImageSerializer
    pagination_class = ImageCursorPagination

    def get_serializer_context(self):
        plan = self.get_user_plan()
        context = super().get_serializer_context()
        context['include_original_image'] = plan.include_original_image
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = ImageUpload.objects.filter(user=self.request.user)
        return queryset

    def get_user_plan(self):
        user = self.request.user
        if hasattr(user, 'userplan'):
            user_plan = user.userplan
        else:
            raise ValidationError(
                {'userplan': 'This functionality needs subscription to a plan'}
            )
        return user_plan.plan


class ImageExpiringLinkView(ModelViewSet):
    """
    This view presents the expiring links created by a user and APIs to manage them.
    User should have permission to add expiring links to access this feature. User can
    filter on expiring links of an image by using a filter criteria. For eg,
    ```
    /api/expiring-links/?base_image=1
    ```
    """
    serializer_class = ImageExpiringLinkSerializer
    permission_classes = (
        IsAuthenticated,
        HasExpiringLinkPermissions,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('base_image',)

    def get_queryset(self):
        # get records for the user
        return ImageExpiringLink.objects.filter(base_image__user=self.request.user)
