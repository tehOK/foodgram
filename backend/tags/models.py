from django.db import models
from django.core.validators import RegexValidator

slug_validator = RegexValidator(
    regex=r"^[-a-zA-Z0-9_]+$",
    message="Slug может содержать только буквы, цифры, дефисы и подчеркивания.",
)


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=32, unique=True, validators=[slug_validator])

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def __str__(self):
        return self.name
