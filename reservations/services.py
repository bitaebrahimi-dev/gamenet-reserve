from django.core.exceptions import ValidationError
from .workflow import can_transition
from .models import Reservation, ReservationHistory
from django.db import transaction

from .validators import (
    validate_device_availability,
    validate_reservation_date,
    validate_reservation_time,
    validate_reservation_conflict,
)


def create_reservation(
        user,
        device,
        reservation_date,
        start_time,
        end_time
):
    reservation = Reservation(
        user=user,
        device=device,
        reservation_date=reservation_date,
        start_time=start_time,
        end_time=end_time
    )

    validate_device_availability(device)

    validate_reservation_date(reservation)

    validate_reservation_time(reservation)

    validate_reservation_conflict(
        reservation,
        device
    )

    reservation.save()

    return reservation

def update_reservation_status(
        reservation,
        status,
        user,
        reason=''
):
    if not can_transition(
            reservation.status,
            status
    ):
        raise ValidationError(
            'تغییر وضعیت رزرو مجاز نیست.'
        )

    old_status = reservation.status

    with transaction.atomic():
        reservation.status = status

        reservation.save(
            update_fields=['status']
        )

        ReservationHistory.objects.create(
            reservation=reservation,
            old_status=old_status,
            new_status=status,
            changed_by=user,
            reason=reason
        )

    return reservation


def cancel_reservation_by_customer(
        reservation,
        user
):
    if reservation.user != user:
        raise ValidationError(
            'شما اجازه لغو این رزرو را ندارید.'
        )

    if reservation.status != 'pending':
        raise ValidationError(
            'این رزرو قابل لغو نیست.'
        )

    update_reservation_status(
        reservation=reservation,
        status='cancelled',
        user=user,
        reason='لغو توسط مشتری'
    )

    return reservation
