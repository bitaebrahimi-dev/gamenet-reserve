from django.urls import path
from .views import device_list, device_detail, device_create


urlpatterns = [
    path('', device_list, name='device_list'),
    path('<int:device_id>/', device_detail, name='device_detail'),
    path(
        'create/',
        device_create,
        name='device_create'
),
]