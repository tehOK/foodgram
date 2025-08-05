import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(method="filter_tags")
    author = django_filters.NumberFilter(field_name="author")
    tags__name = django_filters.CharFilter(
        field_name="tags__name", lookup_expr="iexact"
    )
    is_in_shopping_cart = django_filters.CharFilter(
        method="filter_in_shopping_cart"
    )
    is_favorited = django_filters.CharFilter(method="filter_favorited")

    def filter_tags(self, queryset, name, value):
        tags = self.request.GET.getlist("tags")
        if tags:
            return queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value == "1" and user.is_authenticated:
            return queryset.filter(shopping_cart=user)
        return queryset

    def filter_favorited(self, queryset, name, value):
        user = self.request.user
        if value == "1" and user.is_authenticated:
            return queryset.filter(favorited=user)
        return queryset

    class Meta:
        model = Recipe
        fields = [
            "is_in_shopping_cart",
            "author",
            "tags__name",
            "tags",
            "is_favorited",
        ]
