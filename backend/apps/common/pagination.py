from rest_framework.pagination import CursorPagination, PageNumberPagination


class IdCursorPagination(CursorPagination):
    """Курсор по убыванию id (для сообщений)."""

    ordering = "-id"
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 100


class SmallPagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50
