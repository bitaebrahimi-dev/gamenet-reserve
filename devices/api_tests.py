from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Device
from django.contrib.auth.models import Permission, User

class DeviceListApiPermissionTests(APITestCase):

    def setUp(self):
        self.url = reverse("device_list_api")
        self.data = {
            "name": "Test PS5",
            "device_type": "PS5",
            "hourly_price": 100000,
        }

    def test_anonymous_cannot_create_device(self):
        create_response = self.client.post(
            self.url,
            self.data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            403
        )
        self.assertEqual(
            Device.objects.count(),
            0
        )
    def test_customer_without_permission_cannot_create_device(self):
        user = User.objects.create_user(username="customer", password="12345678")
        self.client.force_authenticate(user=user)
        create_response = self.client.post(
            self.url,
            self.data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            403
        )
        self.assertEqual(
            Device.objects.count(),
            0
        )

    def test_manager_with_permission_can_create_device(self):
        manager = User.objects.create_user(username="bita", password="98769876")
        permission = Permission.objects.get(codename="add_device")
        manager.user_permissions.add(permission)
        self.client.force_authenticate(user=manager)
        create_response = self.client.post(
            self.url,
            self.data,
            format='json'
        )
        self.assertEqual(
            create_response.status_code,
            201
        )
        self.assertEqual(
            Device.objects.count(),
            1
        )
    def test_manager_with_invalid_data_cannot_create_device(self):
        manager = User.objects.create_user(username="bita", password="98769876")
        permission = Permission.objects.get(codename="add_device")
        manager.user_permissions.add(permission)
        self.client.force_authenticate(user=manager)
        bad_data = {**self.data, "hourly_price": -100}
        create_response = self.client.post(
            self.url,
            bad_data,
            format='json'
        )
        self.assertEqual(
            create_response.status_code,
            400
        )
        self.assertEqual(
            Device.objects.count(),
            0
        )


