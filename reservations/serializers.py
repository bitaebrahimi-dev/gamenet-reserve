from rest_framework import serializers

from .models import Reservation, ReservationHistory

class ReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation

        fields = [
            "id",
            "user",
            "device",
            "reservation_date",
            "start_time",
            "end_time",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "device",
            "status",
            "created_at",
        ]


class ReservationStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Reservation.STATUS_CHOICES
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default=""
    )


class ReservationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationHistory
        fields = [
            "id",
            "reservation",
            "old_status",
            "new_status",
            "changed_by",
            "reason",
            "created_at",
        ]
