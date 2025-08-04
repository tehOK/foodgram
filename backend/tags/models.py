from django.core.validators import RegexValidator
from django.db import models

from tags.constants import NAME_LENGTH, SLUG_LENGTH, SLUG_REGEX

slug_validator = RegexValidator(
    regex=SLUG_REGEX,
    message="Может содержать только буквы, цифры, дефисы и подчеркивания.",
)


class Tag(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, unique=True)
    slug = models.SlugField(
        max_length=SLUG_LENGTH, unique=True, validators=[slug_validator]
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name
