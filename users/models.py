from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model with indexed email for performance."""
    email = models.EmailField(unique=True, db_index=True)

    def __str__(self):
        return self.username
