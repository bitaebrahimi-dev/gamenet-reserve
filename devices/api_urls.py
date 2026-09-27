from django.urls import path

from .views import (
    device_list_api,
    device_detail_api,
)

urlpatterns = [
    path(
        "",
        device_list_api,
        name="device_list_api",
    ),
    path(
        "<int:device_id>/",
        device_detail_api,
        name="device_detail_api",
    ),
]
