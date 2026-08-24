from django.db import models
from django.contrib.auth.models import User
from devices.models import Device


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار تأیید'),
        ('confirmed', 'تأیید شده'),
        ('cancelled', 'لغو شده'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='کاربر'
    )

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        verbose_name='دستگاه'
    )

    reservation_date = models.DateField(
        verbose_name='تاریخ رزرو'
    )

    start_time = models.TimeField(
        verbose_name='ساعت شروع'
    )

    end_time = models.TimeField(
        verbose_name='ساعت پایان'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت رزرو'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان ثبت رزرو'
    )

    def __str__(self):
        return f'{self.user.username} - {self.device.name}'