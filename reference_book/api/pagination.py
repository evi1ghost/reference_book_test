from rest_framework.pagination import PageNumberPagination


PAGINATE_BY = 10


class ResultsSetPagination(PageNumberPagination):
    page_size = PAGINATE_BY
    page_size_query_param = 'page_size'
    max_page_size = 100
