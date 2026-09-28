from django.urls import path

from .views import reservation_create_api


urlpatterns = [
    path(
        "devices/<int:device_id>/reservations/",
        reservation_create_api,
        name="reservation_create_api",
    ),
]
