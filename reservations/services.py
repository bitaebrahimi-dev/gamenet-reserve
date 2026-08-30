from .models import Reservation
from django.core.exceptions import ValidationError
from django.utils import timezone


def create_reservation(form, user, device):
    reservation = form.save(commit=False)

    if reservation.reservation_date < timezone.localdate():
        raise ValidationError(
            'تاریخ رزرو نمی‌تواند گذشته باشد.'
        )

    if reservation.end_time <= reservation.start_time:
        raise ValidationError(

            'ساعت پایان باید بعد از ساعت شروع باشد.'
        )

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

    reservation.user = user
    reservation.device = device

    reservation.save()

    return reservation


def update_reservation_status(reservation, status):
    if status not in ['confirmed', 'cancelled']:
        raise ValidationError(
            'وضعیت انتخاب شده معتبر نیست.'
        )
    if reservation.status != 'pending':
        raise ValidationError(
            'این رزرو قبلاً تعیین تکلیف شده است.'
        )
    reservation.status = status
    reservation.save(update_fields=['status'])

    return reservation
