from django.shortcuts import render, get_object_or_404
from .models import Device


def device_detail(request, device_id):
    device = get_object_or_404(Device, id=device_id)

    return render(
        request,
        'devices/device_detail.html',
        {'device': device}
    )


def device_list(request):
    devices = Device.objects.all()

    return render(
        request,
        'devices/device_list.html',
        {'devices': devices}
    )
