from django.test import TestCase
from .models import Device
from .forms import DeviceForm
from django.contrib.auth.models import Permission, User
from django.urls import reverse


class DeviceTestCase(TestCase):

    def test_create_device_success(self):
        form_data = {
            'name': 'Test PS5',
            'device_type': 'PS5',
            'hourly_price': 100000,
            'description': 'دستگاه تست',
            'is_active': True,
        }

        form = DeviceForm(form_data)

        self.assertTrue(
            form.is_valid()
        )

        device = form.save()

        self.assertEqual(
            Device.objects.count(),
            1
        )

        self.assertEqual(
            device.name,
            'Test PS5'
        )

        self.assertEqual(
            device.device_type,
            'PS5'
        )

        self.assertEqual(
            device.hourly_price,
            100000
        )

        self.assertTrue(
            device.is_active
        )

    def test_create_device_with_negative_price(self):
        form_data = {
            'name': 'Test PS5',
            'device_type': 'PS5',
            'hourly_price': -100000,
            'description': 'دستگاه تست',
            'is_active': True,
        }

        form = DeviceForm(form_data)

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            'hourly_price',
            form.errors
        )

        self.assertEqual(
            Device.objects.count(),
            0
        )

    def test_device_default_is_active_true(self):
        device = Device.objects.create(
            name='Default Active PS5',
            device_type='PS5',
            hourly_price=100000,
        )

        self.assertTrue(
            device.is_active
        )

    def test_device_list_shows_only_active_devices_for_normal_user(self):
        active_device = Device.objects.create(
            name='Active PS5',
            device_type='PS5',
            hourly_price=100000,
            is_active=True
        )

        inactive_device = Device.objects.create(
            name='Inactive PS5',
            device_type='PS5',
            hourly_price=100000,
            is_active=False
        )

        response = self.client.get(
            reverse('device_list')
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            active_device.name
        )

        self.assertNotContains(
            response,
            inactive_device.name
        )

    def test_manager_can_see_all_devices(self):
        manager = User.objects.create_user(
            username='manager',
            password='12345678'
        )

        permission = Permission.objects.get(
            codename='change_device'
        )

        manager.user_permissions.add(
            permission
        )

        active_device = Device.objects.create(
            name='Active PS5',
            device_type='PS5',
            hourly_price=100000,
            is_active=True
        )

        inactive_device = Device.objects.create(
            name='Inactive PS5',
            device_type='PS5',
            hourly_price=100000,
            is_active=False
        )

        self.client.login(
            username='manager',
            password='12345678'
        )

        response = self.client.get(
            reverse('device_list')
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            active_device.name
        )

        self.assertContains(
            response,
            inactive_device.name
        )

    def test_normal_user_can_see_active_device_detail_only(self):
        active_device = Device.objects.create(
            name='Active PS5',
            device_type='PS5',
            hourly_price=100000,
            is_active=True
        )

        inactive_device = Device.objects.create(
            name='Inactive PS5',
            device_type='PS5',
            hourly_price=100000,
            is_active=False
        )

        response = self.client.get(
            reverse(
                'device_detail',
                args=[active_device.id]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            active_device.name
        )

        response = self.client.get(
            reverse(
                'device_detail',
                args=[inactive_device.id]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_manager_can_update_device(self):
        manager = User.objects.create_user(
            username='manager',
            password='12345678'
        )

        permission = Permission.objects.get(
            codename='change_device'
        )

        manager.user_permissions.add(
            permission
        )

        device = Device.objects.create(
            name='Old PS5',
            device_type='PS5',
            hourly_price=100000,
            description='Old description',
            is_active=True
        )

        self.client.login(
            username='manager',
            password='12345678'
        )

        form_data = {
            'name': 'Updated PS5',
            'device_type': 'PS5',
            'hourly_price': 150000,
            'description': 'Updated description',
            'is_active': True,
        }

        response = self.client.post(
            reverse(
                'device_update',
                args=[device.id]
            ),
            data=form_data
        )

        self.assertEqual(
            response.status_code,
            302
        )

        device.refresh_from_db()

        self.assertEqual(
            device.name,
            'Updated PS5'
        )

        self.assertEqual(
            device.hourly_price,
            150000
        )

        self.assertEqual(
            device.description,
            'Updated description'
        )

    def test_normal_user_cannot_update_device_without_permission(self):
        user = User.objects.create_user(
            username='normal_user',
            password='12345678'
        )

        device = Device.objects.create(
            name='Old PS5',
            device_type='PS5',
            hourly_price=100000,
            description='Old description',
            is_active=True
        )

        self.client.login(
            username='normal_user',
            password='12345678'
        )

        form_data = {
            'name': 'Hacked PS5',
            'device_type': 'PS5',
            'hourly_price': 500000,
            'description': 'Changed without permission',
            'is_active': False,
        }

        response = self.client.post(
            reverse(
                'device_update',
                args=[device.id]
            ),
            data=form_data
        )

        self.assertEqual(
            response.status_code,
            403
        )

        device.refresh_from_db()

        self.assertEqual(
            device.name,
            'Old PS5'
        )

        self.assertEqual(
            device.hourly_price,
            100000
        )

        self.assertTrue(
            device.is_active
        )

    def test_user_without_add_permission_cannot_create_device(self):
        user = User.objects.create_user(
            username='normal_user',
            password='12345678'
        )

        self.client.login(
            username='normal_user',
            password='12345678'
        )

        form_data = {
            'name': 'Unauthorized PS5',
            'device_type': 'PS5',
            'hourly_price': 120000,
            'description': 'Unauthorized device',
            'is_active': True,
        }

        response = self.client.post(
            reverse('device_create'),
            data=form_data
        )

        self.assertEqual(
            response.status_code,
            403
        )

        self.assertEqual(
            Device.objects.count(),
            0
        )

    def test_anonymous_user_cannot_create_device(self):
        form_data = {
            'name': 'Anonymous PS5',
            'device_type': 'PS5',
            'hourly_price': 120000,
            'description': 'Anonymous device',
            'is_active': True,
        }

        response = self.client.post(
            reverse('device_create'),
            data=form_data
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertEqual(
            Device.objects.count(),
            0
        )

    def test_anonymous_user_cannot_update_device(self):
        device = Device.objects.create(
            name='Old PS5',
            device_type='PS5',
            hourly_price=100000,
            description='Old description',
            is_active=True
        )

        form_data = {
            'name': 'Hacked PS5',
            'device_type': 'PS5',
            'hourly_price': 500000,
            'description': 'Changed by anonymous user',
            'is_active': False,
        }

        response = self.client.post(
            reverse(
                'device_update',
                args=[device.id]
            ),
            data=form_data
        )

        self.assertEqual(
            response.status_code,
            302
        )

        device.refresh_from_db()

        self.assertEqual(
            device.name,
            'Old PS5'
        )

        self.assertEqual(
            device.hourly_price,
            100000
        )

        self.assertTrue(
            device.is_active
        )

    def test_manager_cannot_update_device_with_invalid_data(self):
        manager = User.objects.create_user(
            username='manager_invalid_update',
            password='12345678'
        )

        permission = Permission.objects.get(
            codename='change_device'
        )

        manager.user_permissions.add(
            permission
        )

        device = Device.objects.create(
            name='Old PS5',
            device_type='PS5',
            hourly_price=100000,
            description='Old description',
            is_active=True
        )

        self.client.login(
            username='manager_invalid_update',
            password='12345678'
        )

        form_data = {
            'name': 'Updated PS5',
            'device_type': 'PS5',
            'hourly_price': -500000,
            'description': 'Invalid price update',
            'is_active': True,
        }

        response = self.client.post(
            reverse(
                'device_update',
                args=[device.id]
            ),
            data=form_data
        )

        self.assertEqual(
            response.status_code,
            200
        )

        device.refresh_from_db()

        self.assertEqual(
            device.name,
            'Old PS5'
        )

        self.assertEqual(
            device.hourly_price,
            100000
        )

        self.assertEqual(
            device.description,
            'Old description'
        )

        self.assertTrue(
            device.is_active
        )