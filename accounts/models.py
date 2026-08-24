from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    phone = models.CharField(
        max_length=11,
        blank=True
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    birth_date = models.DateField(
        blank=True,
        null=True
    )

    ROLE_CHOICES = [
        ('CUSTOMER', 'مشتری'),
        ('MANAGER', 'مدیر'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER'
    )

    def __str__(self):
        return self.user.username
