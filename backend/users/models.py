from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from recipes.models import Recipe
from users.constans import EMAIL_MAX_LENGTH


class FoodgramUser(AbstractUser):
    """Модель пользователя Foodgram."""

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        verbose_name="Avatar",
    )
    is_favorited = models.ManyToManyField(
        Recipe,
        blank=True,
        verbose_name="Избранные рецепты",
        related_name="favorited",
    )
    is_in_shopping_cart = models.ManyToManyField(
        Recipe,
        blank=True,
        related_name="shopping_cart",
        verbose_name="Корзина покупок",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Почта",
    )
    password = models.CharField(
        verbose_name="Пароль", blank=False, max_length=EMAIL_MAX_LENGTH
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        default_related_name = "users"

    def has_favorite(self, recipe):
        """Проверить, есть ли рецепт в избранном."""
        return self.is_favorited.filter(id=recipe.id).exists()

    def has_in_cart(self, recipe):
        """Проверить, есть ли рецепт в корзине покупок."""
        return self.is_in_shopping_cart.filter(id=recipe.id).exists()

    def subscribe(self, user):
        """Подписаться на другого пользователя."""
        Subscription.objects.get_or_create(subscriber=self, author=user)

    def unsubscribe(self, user):
        """Отписаться от другого пользователя."""
        Subscription.objects.filter(subscriber=self, author=user).delete()

    def is_subscribed(self, user):
        """Проверить, подписан ли пользователь на другого."""
        return Subscription.objects.filter(
            subscriber=self, author=user
        ).exists()

    @property
    def followers(self):
        """Вернуть queryset пользователей, которые подписаны на пользователя"""
        return User.objects.filter(subscriptions__author=self)

    @property
    def all_subscriptions(self):
        """Вернуть queryset пользователей, на которых подписан пользователь."""
        return self.subscriptions.all()

    @property
    def favorited(self):
        """Получить избранные рецепты пользователя."""
        return self.is_favorited.all()

    @property
    def shopping_cart(self):
        """Получить рецепты в корзине покупок пользователя."""
        return self.is_in_shopping_cart.all()


User = get_user_model()


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        related_name="subscribers",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )

    class Meta:
        unique_together = ("subscriber", "author")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        default_related_name = "subscriptions"

    def __str__(self):
        return f"{self.subscriber} подписан на {self.author}"
