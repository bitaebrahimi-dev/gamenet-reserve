from django.db import models
from django.contrib.auth.models import User
from devices.models import Device
from django.conf import settings


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



class ReservationHistory(models.Model):

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='رزرو'
    )

    old_status = models.CharField(
        max_length=20,
        verbose_name='وضعیت قبلی'
    )

    new_status = models.CharField(
        max_length=20,
        verbose_name='وضعیت جدید'
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='تغییر توسط'
    )

    reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='دلیل تغییر'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان تغییر'
    )


    def __str__(self):
        return (
            f'{self.reservation} '
            f'{self.old_status} → {self.new_status}'
        )