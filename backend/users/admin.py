from django.contrib import admin

from users.constans import ADMIN_PAGE_SIZE
from users.models import FoodgramUser


@admin.register(FoodgramUser)
class FoodgramUserAdmin(admin.ModelAdmin):
    """Админка для управления пользователями Foodgram."""

    list_display = ("username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_active")
    ordering = ("username",)
    list_per_page = ADMIN_PAGE_SIZE
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Разрешения", {"fields": ("is_staff", "is_active")}),
        (
            "Личная информация",
            {"fields": ("first_name", "last_name", "avatar")},
        ),
        ("Рецепты", {"fields": ("get_user_recipes",)}),
        ("Подписки", {"fields": ("get_subscriptions", "get_followers")}),
        ("Корзина покупок", {"fields": ("get_shopping_cart",)}),
        ("Избранные рецепты", {"fields": ("get_favorited",)}),
    )
    readonly_fields = (
        "get_favorited",
        "get_shopping_cart",
        "get_subscriptions",
        "get_followers",
        "get_user_recipes",
    )

    @admin.display(description="Рецепты пользователя")
    def get_user_recipes(self, obj):
        """Получить рецепты, созданные пользователем."""
        return (
            ", ".join([recipe.name for recipe in obj.recipes.all()])
            if obj.recipes.exists()
            else "Нет рецептов"
        )

    @admin.display(description="Подписчики")
    def get_followers(self, obj):
        """Получить подписчиков пользователя."""
        return (
            ", ".join([user.username for user in obj.followers])
            if obj.followers
            else "Нет подписчиков"
        )

    @admin.display(description="Подписки")
    def get_subscriptions(self, obj):
        """Получить подписки пользователя."""
        return (
            ", ".join(
                [user.author.username for user in obj.all_subscriptions]
            )
            if obj.all_subscriptions
            else "Нет подписок"
        )

    @admin.display(description="Корзина покупок")
    def get_shopping_cart(self, obj):
        """Получить рецепты в корзине покупок пользователя."""
        return (
            ", ".join(
                [recipe.name for recipe in obj.shopping_cart]
            ) if obj.shopping_cart else "Нет рецептов в корзине"
        )

    @admin.display(description="Избранные рецепты")
    def get_favorited(self, obj):
        """Получить избранные рецепты пользователя."""
        return (
            ", ".join([recipe.name for recipe in obj.favorited])
            if obj.favorited
            else "Нет избранных рецептов"
        )
