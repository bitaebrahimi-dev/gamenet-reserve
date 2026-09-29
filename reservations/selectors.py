from .models import Reservation, ReservationHistory


def get_user_reservations(user):
    return Reservation.objects.filter(
        user=user
    )


def get_all_reservations():
    return Reservation.objects.all()


def get_user_reservation(user, reservation_id):
    return Reservation.objects.filter(
        user=user,
        id=reservation_id
    ).first()


def get_reservation_history(reservation):
    return ReservationHistory.objects.filter(
        reservation=reservation
    ).order_by("created_at")
