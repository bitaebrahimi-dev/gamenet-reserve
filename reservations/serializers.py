from rest_framework import serializers

from .models import Reservation


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

