from django.urls import path

from .views import (
    device_list,
    device_detail,
    device_create,
    device_update,
    device_list_api
)

urlpatterns = [

    path(
        '',
        device_list,
        name='device_list'
    ),

    path(
        'create/',
        device_create,
        name='device_create'
    ),

    path(
        '<int:device_id>/edit/',
        device_update,
        name='device_update'
    ),

    path(
        '<int:device_id>/',
        device_detail,
        name='device_detail'
    ),
    path(
        "api/devices/",
        device_list_api,
        name="device_list_api"
    ),
]
