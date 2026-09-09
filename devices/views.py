from django.shortcuts import render, get_object_or_404, redirect
from .models import Device
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required
)
from .forms import DeviceForm


def device_detail(request, device_id):

    if request.user.has_perm('devices.change_device'):

        device = get_object_or_404(
            Device,
            id=device_id
        )

    else:

        device = get_object_or_404(
            Device,
            id=device_id,
            is_active=True
        )

    return render(
        request,
        'devices/device_detail.html',
        {'device': device}
    )


def device_list(request):
    if request.user.has_perm('devices.change_device'):
        devices = Device.objects.all()
    else:
        devices = Device.objects.filter(
            is_active=True
        )

    return render(
        request,
        'devices/device_list.html',
        {'devices': devices}
    )


@login_required
@permission_required(
    'devices.add_device',
    raise_exception=True
)
def device_create(request):
    if request.method == 'POST':

        form = DeviceForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'دستگاه با موفقیت اضافه شد.'
            )

            return redirect(
                'device_list'
            )

    else:

        form = DeviceForm()

    return render(
        request,
        'devices/device_form.html',
        {'form': form}
    )


@login_required
@permission_required(
    'devices.change_device',
    raise_exception=True
)
def device_update(request, device_id):
    device = get_object_or_404(
        Device,
        id=device_id
    )

    if request.method == 'POST':

        form = DeviceForm(
            request.POST,
            instance=device
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'دستگاه با موفقیت ویرایش شد.'
            )

            return redirect(
                'device_list'
            )

    else:

        form = DeviceForm(
            instance=device
        )

    return render(
        request,
        'devices/device_form.html',
        {'form': form}
    )
