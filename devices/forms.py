from django import forms
from .models import Device


class DeviceForm(forms.ModelForm):

    class Meta:
        model = Device

        fields = [
            'name',
            'device_type',
            'hourly_price',
            'description',
            'is_active',
        ]