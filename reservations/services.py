from django.core.exceptions import ValidationError
from .workflow import can_transition

from .validators import (
    validate_device_availability,
    validate_reservation_date,
    validate_reservation_time,
    validate_reservation_conflict,
)

def create_reservation(form, user, device):
    reservation = form.save(commit=False)

    validate_device_availability(device)

    validate_reservation_date(reservation)

    validate_reservation_time(reservation)

    validate_reservation_conflict(
        reservation,
        device
    )
    # اتصال اطلاعات رزرو
    reservation.user = user
    reservation.device = device

    # ذخیره رزرو
    reservation.save()

    return reservation


def update_reservation_status(reservation, status):

    if not can_transition(
        reservation.status,
        status
    ):
        raise ValidationError(
            'تغییر وضعیت رزرو مجاز نیست.'
        )


    reservation.status = status

    reservation.save(
        update_fields=['status']
    )

    return reservation
