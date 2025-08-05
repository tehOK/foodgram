from django.contrib import admin

from users import user_utils as us
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
    def get_user_recipes(self, user):
        """Получить рецепты, созданные пользователем."""
        return (
            ", ".join([recipe.name for recipe in user.recipes.all()])
            if user.recipes.exists()
            else "Нет рецептов"
        )

    @admin.display(description="Подписчики")
    def get_followers(self, user):
        """Получить подписчиков пользователя."""
        return (
            ", ".join(
                [
                    follower.subscriber.username
                    for follower in us.followers(user)
                ]
            )
            if us.followers(user)
            else "Нет подписчиков"
        )

    @admin.display(description="Подписки")
    def get_subscriptions(self, user):
        """Получить подписки пользователя."""
        return (
            ", ".join(
                [
                    subscription.author.username
                    for subscription in us.all_subscriptions(user)
                ]
            )
            if us.all_subscriptions(user)
            else "Нет подписок"
        )

    @admin.display(description="Корзина покупок")
    def get_shopping_cart(self, user):
        """Получить рецепты в корзине покупок пользователя."""
        return (
            ", ".join([recipe.name for recipe in us.shopping_cart(user)])
            if us.shopping_cart(user)
            else "Нет рецептов в корзине"
        )

    @admin.display(description="Избранные рецепты")
    def get_favorited(self, user):
        """Получить избранные рецепты пользователя."""
        return (
            ", ".join([recipe.name for recipe in us.favorited(user)])
            if us.favorited(user)
            else "Нет избранных рецептов"
        )
