from django.db import models


class Recipe(models.Model):
    ingredients = models.ManyToManyField("ingredients.Ingredient")
    tags = models.ManyToManyField("tags.Tag")
    image = models.ImageField(upload_to="recipes/images/")
    name = models.CharField(max_length=255)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField(
        help_text="Время приготовления (в минутах)"
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        default_related_name = "recipes"

    def __str__(self):
        return self.name
