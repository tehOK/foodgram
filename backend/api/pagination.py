from rest_framework.pagination import PageNumberPagination


class FoodgramRecipePagination(PageNumberPagination):
    page_size_query_param = "limit"
    page_query_param = "page"
    max_page_size = 20

    def get_page_size(self, request):
        try:
            return int(
                request.query_params.get(
                    self.page_size_query_param, self.page_size
                )
            )
        except (KeyError, ValueError, TypeError):
            return self.page_size
