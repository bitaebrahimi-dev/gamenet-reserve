from rest_framework.permissions import BasePermission

class CanViewAllReservations(BasePermission):

    def has_permission(self, request, view):
        return request.user.has_perm(
            "reservations.can_view_all_reservations"
        )

class CanChangeReservationStatus(BasePermission):

    def has_permission(self, request, view):
        return request.user.has_perm(
            "reservations.can_change_reservation_status"
        )