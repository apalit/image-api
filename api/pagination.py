from rest_framework.pagination import CursorPagination


class ImageCursorPagination(CursorPagination):
    ordering = '-create_date_time'
