from django.contrib import admin

from tags.constants import ADMIN_PAGE_SIZE
from tags.models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = ADMIN_PAGE_SIZE
