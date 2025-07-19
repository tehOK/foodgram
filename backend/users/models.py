from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class FoodgramUser(AbstractUser):
    """Model representing a user in the Foodgram application."""

    is_subscribed = models.BooleanField(
        default=False,  # Indicates if the user is subscribed to any other user
        verbose_name='Is Subscribed',
    )
    avatar = models.ImageField(
        upload_to='avatars/',  # Directory where user avatars will be stored
        blank=True,  # Allows the field to be optional
        verbose_name='Avatar',
    )

    class Meta:
        verbose_name = 'Foodgram User'
        verbose_name_plural = 'Foodgram Users'