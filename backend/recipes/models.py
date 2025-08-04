import shortuuid
from django.db import models

from ingredients.models import Ingredient
from recipes.constants import DEFAULT_AMOUNT, NAME_LENGTH, SLUG_LENGTH
from tags.models import Tag


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredientAmount",
        verbose_name="Ингридиенты",
    )
    author = models.ForeignKey(
        "users.FoodgramUser", on_delete=models.CASCADE, verbose_name="Автор"
    )
    tags = models.ManyToManyField(
        Tag, through="RecipeTags", verbose_name="Тег"
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Изображение рецепта",
        blank=True,
    )
    name = models.CharField(
        max_length=NAME_LENGTH, verbose_name="Название рецепта"
    )
    text = models.TextField(verbose_name="Описание рецепта")
    cooking_time = models.PositiveIntegerField(
        help_text="Время приготовления (в минутах)",
        verbose_name="Время приготовления (минуты)",
    )
    slug = models.CharField(
        max_length=SLUG_LENGTH,
        help_text="Уникальный идентификатор рецепта",
        unique=True,
        blank=True,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        help_text="Дата и время публикации рецепта",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = shortuuid.ShortUUID().random(length=SLUG_LENGTH)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        default_related_name = "recipes"

    def __str__(self):
        return self.name


class RecipeIngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент"
    )
    amount = models.PositiveIntegerField(
        help_text="Количество ингредиента",
        default=DEFAULT_AMOUNT,
        verbose_name="Количество ингредиента",
    )

    class Meta:
        unique_together = ("recipe", "ingredient")
        default_related_name = "recipe_ingredients"

    def __str__(self):
        return f"{self.ingredient.name}"


class RecipeTags(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт"
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name="Тег")

    class Meta:
        unique_together = ("recipe", "tag")
        default_related_name = "recipe_tags"

    def __str__(self):
        return f"{self.tag.name}"
