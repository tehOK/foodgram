from django.contrib import admin

from recipes.constants import ADMIN_PAGE_SIZE
from recipes.models import Recipe, RecipeIngredientAmount, RecipeTags


class RecipeIngredientAmountInline(admin.TabularInline):
    model = RecipeIngredientAmount
    extra = 1
    verbose_name = "Ингредиенты и их количество"
    verbose_name_plural = "Ингредиенты и их количество"


class TagInline(admin.TabularInline):
    model = RecipeTags
    extra = 1
    verbose_name = "Теги"
    verbose_name_plural = "Теги"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author")
    search_fields = ("name", "author__username")
    list_filter = ("tags", "author")
    filter_horizontal = ("tags",)
    list_per_page = ADMIN_PAGE_SIZE
    readonly_fields = ("subscribers_count",)
    fieldsets = (
        (
            None,
            {"fields": ("name", "author", "image", "text", "cooking_time")},
        ),
        ("Подписчики", {"fields": ("subscribers_count",)}),
    )
    inlines = [RecipeIngredientAmountInline, TagInline]
    readonly_fields = ("subscribers_count",)

    @admin.display(description="Количество подписчиков")
    def subscribers_count(self, obj):
        """Количество подписчиков на рецепт."""
        return obj.favorited.count() if obj.favorited else 0
