from django.urls import path

from .views import (
    reservation_create_api,
    cancel_reservation_api,
    update_reservation_status_api,
    my_reservations_api,
    reservation_detail_api,
    all_reservations_api,
    reservation_history_api,
)

urlpatterns = [
    path(
        "devices/<int:device_id>/reservations/",
        reservation_create_api,
        name="reservation_create_api",
    ),
    path(
        "reservations/<int:reservation_id>/cancel/",
        cancel_reservation_api,
        name="cancel_reservation_api",
    ),
    path(
        "reservations/<int:reservation_id>/status/",
        update_reservation_status_api,
        name="update_reservation_status_api",
    ),
    path(
        "reservations/my/",
        my_reservations_api,
        name="my_reservations_api",
    ),
    path(
        "reservations/<int:reservation_id>/",
        reservation_detail_api,
        name="reservation_detail_api",
    ),
    path(
        "reservations/all/",
        all_reservations_api,
        name="all_reservations_api",
    ),
    path(
        "reservations/<int:reservation_id>/history/",
        reservation_history_api,
        name="reservation_history_api",
    ),
]

