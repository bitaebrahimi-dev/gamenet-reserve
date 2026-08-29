from django.shortcuts import render, get_object_or_404, redirect
from .forms import ReservationForm
from devices.models import Device
from django.contrib import messages
from .models import Reservation
from django.contrib.auth.decorators import login_required
from accounts.decorators import manager_required
from .services import create_reservation
from django.core.exceptions import ValidationError



@login_required
def reservation_create(request, device_id):
    device = get_object_or_404(Device, id=device_id)

    if request.method == 'POST':

        form = ReservationForm(request.POST)

        if form.is_valid():

            try:

                create_reservation(
                    form=form,
                    user=request.user,
                    device=device
                )

                messages.success(
                    request,
                    'رزرو شما با موفقیت ثبت شد.'
                )

                return redirect(
                    'device_detail',
                    device.id
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e
                )

    else:

        form = ReservationForm()

    return render(
        request,
        'reservations/reservation_form.html',
        {'form': form}
    )


@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(
        user=request.user
    )

    return render(
        request,
        'reservations/my_reservations.html',
        {'reservations': reservations}
    )


@manager_required
def all_reservations(request):

    reservations = Reservation.objects.all()

    return render(
        request,
        'reservations/all_reservations.html',
        {'reservations': reservations}
    )