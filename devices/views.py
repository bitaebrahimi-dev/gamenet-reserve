from django.shortcuts import render, get_object_or_404, redirect
from .models import Device
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required
)
from .forms import DeviceForm
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import DeviceSerializer
from rest_framework import status


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


@api_view(["GET", "POST"])
def device_list_api(request):
    if request.method == "GET":
        if request.user.has_perm('devices.change_device'):
            devices = Device.objects.all()
        else:
            devices = Device.objects.filter(
                is_active=True
            )

        serializer = DeviceSerializer(
            devices,
            many=True
        )

        return Response(serializer.data)

    if request.method == "POST":
        serializer = DeviceSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET", "PATCH"])
def device_detail_api(request, device_id):
    if request.method == "GET":
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

        serializer = DeviceSerializer(device)

        return Response(serializer.data)

    if request.method == "PATCH":
        if not request.user.has_perm('devices.change_device'):
            return Response(
                {
                    "detail": "You do not have permission to update this device."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        device = get_object_or_404(
            Device,
            id=device_id
        )

        serializer = DeviceSerializer(
            device,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
