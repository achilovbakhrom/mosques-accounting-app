from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 50  # Number of items per page
    page_size_query_param = 'page_size'  # Allow client to set page size via query param
    max_page_size = 200
