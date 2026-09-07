from django.shortcuts import render, get_object_or_404, redirect

from .forms import ReservationForm
from devices.models import Device

from django.contrib import messages
from .models import Reservation

from django.contrib.auth.decorators import (
    login_required,
    permission_required
)

from django.core.exceptions import ValidationError

from .services import (
    create_reservation,
    update_reservation_status,
    cancel_reservation_by_customer,
)


@login_required
def reservation_create(request, device_id):
    device = get_object_or_404(
        Device,
        id=device_id
    )

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


@permission_required(
    'reservations.can_change_reservation_status',
    raise_exception=True
)
@login_required
def update_reservation_status_view(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    if request.method == 'POST':

        status = request.POST.get('status')

        reason = request.POST.get('reason')

        try:

            update_reservation_status(
                reservation=reservation,
                status=status,
                user=request.user,
                reason=reason,
            )

            messages.success(
                request,
                'وضعیت رزرو با موفقیت تغییر کرد.'
            )


        except ValidationError as e:

            messages.error(
                request,
                e.message
            )

    return redirect(
        'all_reservations'
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


@login_required
def cancel_my_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    try:

        cancel_reservation_by_customer(
            reservation=reservation,
            user=request.user
        )

        messages.success(
            request,
            'رزرو شما با موفقیت لغو شد.'
        )


    except ValidationError as e:

        messages.error(
            request,
            e.message
        )

    return redirect(
        'my_reservations'
    )


@permission_required(
    'reservations.can_view_all_reservations',
    raise_exception=True
)
@login_required
def all_reservations(request):
    reservations = Reservation.objects.all()

    return render(
        request,
        'reservations/all_reservations.html',
        {'reservations': reservations}
    )
