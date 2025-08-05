from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

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
        ordering = ("username",)

    def __str__(self):
        return self.username


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
        ordering = ("subscriber",)

    def __str__(self):
        return f"{self.subscriber} подписан на {self.author}"
