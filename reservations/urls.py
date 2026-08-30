from django.urls import path
from .views import (
    reservation_create,
    my_reservations,
    all_reservations,
    update_reservation_status_view
)

urlpatterns = [
    path('create/<int:device_id>/', reservation_create, name='reservation_create'),
    path(
        'my/',
        my_reservations,
        name='my_reservations'
    ),
    path(
        'all/',
        all_reservations,
        name='all_reservations'
    ),
    path(
        'update-status/<int:reservation_id>/',
        update_reservation_status_view,
        name='update_reservation_status'
    ),
]
