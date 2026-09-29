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
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    ReservationSerializer,
    ReservationStatusSerializer,
    ReservationHistorySerializer,
)
from .selectors import (
    get_user_reservations,
    get_all_reservations,
    get_user_reservation,
    get_reservation_history,
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
                    user=request.user,
                    device=device,
                    **form.cleaned_data
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
    reservations = get_user_reservations(
        request.user
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


@login_required
@permission_required(
    'reservations.can_view_all_reservations',
    raise_exception=True
)
def all_reservations(request):
    reservations = get_all_reservations()

    return render(
        request,
        'reservations/all_reservations.html',
        {'reservations': reservations}
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reservation_create_api(request, device_id):
    device = get_object_or_404(
        Device,
        id=device_id
    )

    serializer = ReservationSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        reservation = create_reservation(
            user=request.user,
            device=device,
            **serializer.validated_data
        )

    except ValidationError as e:
        return Response(
            {
                "detail": e.messages[0]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    output_serializer = ReservationSerializer(
        reservation
    )

    return Response(
        output_serializer.data,
        status=status.HTTP_201_CREATED
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_reservation_api(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    try:
        reservation = cancel_reservation_by_customer(
            reservation=reservation,
            user=request.user
        )

    except ValidationError as e:
        return Response(
            {
                "detail": e.messages[0]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    output_serializer = ReservationSerializer(
        reservation
    )

    return Response(
        output_serializer.data,
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_reservation_status_api(request, reservation_id):

    if not request.user.has_perm(
        "reservations.can_change_reservation_status"
    ):
        return Response(
            {
                "detail": "شما اجازه تغییر وضعیت رزرو را ندارید."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    serializer = ReservationStatusSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        reservation = update_reservation_status(
            reservation=reservation,
            status=serializer.validated_data["status"],
            user=request.user,
            reason=serializer.validated_data["reason"],
        )

    except ValidationError as e:
        return Response(
            {
                "detail": e.messages[0]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    output_serializer = ReservationSerializer(
        reservation
    )

    return Response(
        output_serializer.data,
        status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_reservations_api(request):
    reservations = get_user_reservations(
        request.user
    )

    serializer = ReservationSerializer(
        reservations,
        many=True
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reservation_detail_api(request, reservation_id):
    reservation = get_user_reservation(
        request.user,
        reservation_id
    )

    if reservation is None:
        return Response(
            {"detail": "رزرو پیدا نشد."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ReservationSerializer(
        reservation
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def all_reservations_api(request):
    if not request.user.has_perm(
        "reservations.can_view_all_reservations"
    ):
        return Response(
            {"detail": "شما اجازه مشاهده همه رزروها را ندارید."},
            status=status.HTTP_403_FORBIDDEN
        )

    reservations = get_all_reservations()

    serializer = ReservationSerializer(
        reservations,
        many=True
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reservation_history_api(request, reservation_id):
    if not request.user.has_perm(
        "reservations.can_view_all_reservations"
    ):
        return Response(
            {"detail": "شما اجازه مشاهده تاریخچه رزروها را ندارید."},
            status=status.HTTP_403_FORBIDDEN
        )

    reservation = get_object_or_404(
        get_all_reservations(),
        id=reservation_id
    )

    histories = get_reservation_history(
        reservation
    )

    serializer = ReservationHistorySerializer(
        histories,
        many=True
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )
