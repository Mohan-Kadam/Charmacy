from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ASM', 'ASM'),
        ('SCM', 'SCM'),
        ('MSR', 'MSR'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"
