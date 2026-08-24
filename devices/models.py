from django.db import models


class Device(models.Model):
    DEVICE_TYPES = [
        ('PS5', 'PlayStation 5'),
        ('PS4', 'PlayStation 4'),
        ('XBOX', 'Xbox'),
        ('PC', 'Gaming PC'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='نام دستگاه'
    )

    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_TYPES,
        verbose_name='نوع دستگاه'
    )

    hourly_price = models.PositiveIntegerField(
        verbose_name='قیمت هر ساعت'
    )

    description = models.TextField(
        blank=True,
        verbose_name='توضیحات'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال است'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان ثبت'
    )

    def __str__(self):
        return self.name
    