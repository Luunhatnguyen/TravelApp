from rest_framework import pagination


class TourPagination(pagination.PageNumberPagination):
    page_size = 20
    page_query_param = 'page'

class ArticalPagination(pagination.PageNumberPagination):
    page_size = 5