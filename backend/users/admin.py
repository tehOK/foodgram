from django.contrib import admin
from .models import FoodgramUser

# Register your models here.
@admin.register(FoodgramUser)
class FoodgramUserAdmin(admin.ModelAdmin):
    """Admin interface for managing Foodgram users."""

    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_subscribed')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'is_subscribed')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_subscribed')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'avatar')}),
    )