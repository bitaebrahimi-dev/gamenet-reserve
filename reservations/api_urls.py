from django.urls import path

from .views import (
    reservation_create_api,
    cancel_reservation_api,
    update_reservation_status_api,
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
]

