from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from api.serializers import ImageSerializer
from api.models import ImageUpload


def get_user_plan(user):
    if hasattr(user, 'userplan'):
        user_plan = user.userplan
    else:
        raise ValidationError(
            {'userplan': 'This functionality needs subscription to a plan'}
        )
    return user_plan.plan


class ImageCreateListView(APIView):
    parser_classes = (MultiPartParser, FormParser,)
    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer

    def post(self, request, *args, **kwargs):
        try:
            plan = self.get_user_plan()
        except ValidationError as ve:
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        serializer.context['include_original_image'] = plan.include_original_image
        serializer.context['expiring_link'] = plan.expiring_link
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        try:
            plan = self.get_user_plan()
        except ValidationError as ve:
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        serializer.context['include_original_image'] = plan.include_original_image
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        queryset = ImageUpload.objects.filter(user=user)
        # filter on expiry
        queryset = queryset.filter(
            Q(expiry_date_time__isnull=True) |
            Q(expiry_date_time__gt=timezone.now())
        )
        return queryset

    def get_user_plan(self):
        user = self.request.user
        # get user plan
        return get_user_plan(user)


class ImageDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = ImageUpload.objects.filter(user=user)
        # filter on expiry
        queryset = queryset.filter(
            Q(expiry_date_time__isnull=True) |
            Q(expiry_date_time__gt=timezone.now())
        )
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user_plan = get_user_plan(self.request.user)
        context['include_original_image'] = user_plan.include_original_image
        return context
