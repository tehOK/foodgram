from django.contrib import admin

from ingredients.models import Ingredient
from ingredients.constants import ADMIN_PAGE_SIZE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)
    list_per_page = ADMIN_PAGE_SIZE
