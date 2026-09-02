from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Reservation


def validate_reservation_date(reservation):


    if reservation.reservation_date < timezone.localdate():
        raise ValidationError(
            'تاریخ رزرو نمی‌تواند گذشته باشد.'
        )


def validate_reservation_time(reservation):

    if reservation.end_time <= reservation.start_time:
        raise ValidationError(
            'ساعت پایان باید بعد از ساعت شروع باشد.'
        )


def validate_reservation_conflict(reservation, device):

    existing_reservation = Reservation.objects.filter(
        device=device,
        reservation_date=reservation.reservation_date,
        start_time__lt=reservation.end_time,
        end_time__gt=reservation.start_time,
    ).exists()

    if existing_reservation:
        raise ValidationError(
            'این دستگاه در این بازه زمانی قبلاً رزرو شده است.'
        )


def validate_device_availability(device):
    """
    بررسی می‌کند دستگاه قابل رزرو باشد.
    """

    if not device.is_active:
        raise ValidationError(
            'این دستگاه در حال حاضر قابل رزرو نیست.'
        )