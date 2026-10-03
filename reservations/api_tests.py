from datetime import date, time, timedelta

from django.contrib.auth.models import User, Permission
from devices.models import Device
from rest_framework.test import APITestCase
from reservations.models import Reservation

class ReservationAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='api_test_user',
            password='test_password'
        )

        self.device = Device.objects.create(
            name='API Test PS5',
            is_active=True,
            device_type='PS5',
            hourly_price=100000
        )

    def test_create_reservation_success(self):
        url = f'/api/devices/{self.device.id}/reservations/'

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        response = self.client.post(
            url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["user"],
            self.user.id
        )

        self.assertEqual(
            response.data["device"],
            self.device.id
        )

        self.assertEqual(
            response.data["status"],
            "pending"
        )

        self.assertEqual(
            Reservation.objects.count(),
            1
        )

    def test_create_reservation_with_invalid_data(self):
        url = f'/api/devices/{self.device.id}/reservations/'

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        response = self.client.post(
            url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertIn(
            'reservation_date',
            response.data
        )

    def test_create_reservation_anonymous(self):
        url = f'/api/devices/{self.device.id}/reservations/'

        data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        response = self.client.post(
            url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_create_reservation_with_nonexistent_device(self):
        url = '/api/devices/99999/reservations/'

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        response = self.client.post(
            url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_create_reservation_with_conflict(self):
        url = f'/api/devices/{self.device.id}/reservations/'

        self.client.force_authenticate(
            user=self.user
        )

        first_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        first_response = self.client.post(
            url,
            first_data,
            format='json'
        )

        self.assertEqual(
            first_response.status_code,
            201
        )

        second_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(15, 0),
            'end_time': time(17, 0),
        }

        second_response = self.client.post(
            url,
            second_data,
            format='json'
        )

        self.assertEqual(
            second_response.status_code,
            400
        )

    def test_create_reservation_with_inactive_device(self):
        inactive_device = Device.objects.create(
            name='Inactive API PS5',
            is_active=False,
            device_type='PS5',
            hourly_price=100000
        )

        url = f'/api/devices/{inactive_device.id}/reservations/'

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        response = self.client.post(
            url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_update_reservation_status_success(self):
        reservation_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        self.client.force_authenticate(
            user=self.user
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            reservation_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        permission = Permission.objects.get(
            codename='can_change_reservation_status'
        )

        self.user.user_permissions.add(
            permission
        )

        status_url = (
            f'/api/reservations/{reservation_id}/status/'
        )

        status_data = {
            'status': 'confirmed',
            'reason': 'تایید توسط مدیر'
        }

        response = self.client.post(
            status_url,
            status_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data['status'],
            'confirmed'
        )

    def test_update_reservation_status_invalid_transition(self):
        reservation_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        self.client.force_authenticate(
            user=self.user
        )

        permission = Permission.objects.get(
            codename='can_change_reservation_status'
        )

        self.user.user_permissions.add(
            permission
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            reservation_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        status_url = (
            f'/api/reservations/{reservation_id}/status/'
        )

        cancel_data = {
            'status': 'cancelled',
            'reason': 'لغو رزرو برای تست'
        }

        cancel_response = self.client.post(
            status_url,
            cancel_data,
            format='json'
        )

        self.assertEqual(
            cancel_response.status_code,
            200
        )

        invalid_data = {
            'status': 'confirmed',
            'reason': 'تلاش برای تایید رزرو لغوشده'
        }

        response = self.client.post(
            status_url,
            invalid_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_update_reservation_status_without_permission(self):
        reservation_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        self.client.force_authenticate(
            user=self.user
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            reservation_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        status_url = (
            f'/api/reservations/{reservation_id}/status/'
        )

        status_data = {
            'status': 'confirmed',
            'reason': 'تلاش کاربر بدون مجوز'
        }

        response = self.client.post(
            status_url,
            status_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            403
        )
    def test_cancel_reservation_success(self):
        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        self.client.force_authenticate(
            user=self.user
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        cancel_url = (
            f'/api/reservations/{reservation_id}/cancel/'
        )

        response = self.client.post(
            cancel_url
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data['status'],
            'cancelled'
        )

    def test_cancel_other_users_reservation(self):
        other_user = User.objects.create_user(
            username='other_api_user',
            password='12345678'
        )

        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        self.client.force_authenticate(
            user=self.user
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        self.client.force_authenticate(
            user=other_user
        )

        cancel_url = (
            f'/api/reservations/{reservation_id}/cancel/'
        )

        response = self.client.post(
            cancel_url
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_cancel_confirmed_reservation(self):
        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        self.client.force_authenticate(
            user=self.user
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        permission = Permission.objects.get(
            codename='can_change_reservation_status'
        )

        self.user.user_permissions.add(
            permission
        )

        status_url = (
            f'/api/reservations/{reservation_id}/status/'
        )

        status_response = self.client.post(
            status_url,
            {
                'status': 'confirmed',
                'reason': 'تایید برای تست'
            },
            format='json'
        )

        self.assertEqual(
            status_response.status_code,
            200
        )

        cancel_url = (
            f'/api/reservations/{reservation_id}/cancel/'
        )

        cancel_response = self.client.post(
            cancel_url
        )

        self.assertEqual(
            cancel_response.status_code,
            400
        )

    def test_cancel_reservation_anonymous(self):
        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        self.client.force_authenticate(
            user=self.user
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        self.client.force_authenticate(
            user=None
        )

        cancel_url = (
            f'/api/reservations/{reservation_id}/cancel/'
        )

        response = self.client.post(
            cancel_url
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_cancel_reservation_not_found(self):
        self.client.force_authenticate(
            user=self.user
        )

        cancel_url = (
            '/api/reservations/999999/cancel/'
        )

        response = self.client.post(
            cancel_url
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_my_reservations_returns_user_reservations(self):
        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        response = self.client.post(
            create_url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            201
        )

        my_url = '/api/reservations/my/'

        response = self.client.get(
            my_url
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['user'],
            self.user.id
        )

    def test_my_reservations_does_not_return_other_users_reservations(self):
        other_user = User.objects.create_user(
            username='other_my_reservations_user',
            password='12345678'
        )

        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        self.client.force_authenticate(
            user=other_user
        )

        response = self.client.get(
            '/api/reservations/my/'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            0
        )

    def test_my_reservations_anonymous(self):
        response = self.client.get(
            '/api/reservations/my/'
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_reservation_detail_success(self):
        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        detail_url = (
            f'/api/reservations/{reservation_id}/'
        )

        response = self.client.get(
            detail_url
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data['id'],
            reservation_id
        )

        self.assertEqual(
            response.data['user'],
            self.user.id
        )

    def test_reservation_detail_other_user(self):
        other_user = User.objects.create_user(
            username='other_detail_user',
            password='12345678'
        )

        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        self.client.force_authenticate(
            user=other_user
        )

        detail_url = (
            f'/api/reservations/{reservation_id}/'
        )

        response = self.client.get(
            detail_url
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_reservation_detail_not_found(self):
        self.client.force_authenticate(
            user=self.user
        )

        detail_url = (
            '/api/reservations/999999/'
        )

        response = self.client.get(
            detail_url
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_reservation_detail_anonymous(self):
        response = self.client.get(
            '/api/reservations/999999/'
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_all_reservations_with_permission(self):
        permission = Permission.objects.get(
            codename='can_view_all_reservations'
        )

        self.user.user_permissions.add(
            permission
        )

        self.client.force_authenticate(
            user=self.user
        )

        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        response = self.client.get(
            '/api/reservations/all/'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

    def test_all_reservations_without_permission(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            '/api/reservations/all/'
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_all_reservations_anonymous(self):
        response = self.client.get(
            '/api/reservations/all/'
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_reservation_history_with_permission(self):
        change_permission = Permission.objects.get(
            codename='can_change_reservation_status'
        )

        view_permission = Permission.objects.get(
            codename='can_view_all_reservations'
        )

        self.user.user_permissions.add(
            change_permission,
            view_permission
        )

        self.client.force_authenticate(
            user=self.user
        )

        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        status_url = (
            f'/api/reservations/{reservation_id}/status/'
        )

        status_response = self.client.post(
            status_url,
            {
                'status': 'confirmed',
                'reason': 'تایید برای تست تاریخچه'
            },
            format='json'
        )

        self.assertEqual(
            status_response.status_code,
            200
        )

        history_url = (
            f'/api/reservations/{reservation_id}/history/'
        )

        response = self.client.get(
            history_url
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['old_status'],
            'pending'
        )

        self.assertEqual(
            response.data[0]['new_status'],
            'confirmed'
        )

    def test_reservation_history_without_permission(self):
        self.client.force_authenticate(
            user=self.user
        )

        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        history_url = (
            f'/api/reservations/{reservation_id}/history/'
        )

        response = self.client.get(
            history_url
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_reservation_history_not_found(self):
        permission = Permission.objects.get(
            codename='can_view_all_reservations'
        )

        self.user.user_permissions.add(
            permission
        )

        self.client.force_authenticate(
            user=self.user
        )

        history_url = (
            '/api/reservations/999999/history/'
        )

        response = self.client.get(
            history_url
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_reservation_history_anonymous(self):
        response = self.client.get(
            '/api/reservations/999999/history/'
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_update_reservation_status_anonymous(self):
        self.client.force_authenticate(
            user=self.user
        )

        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        self.client.force_authenticate(
            user=None
        )

        status_url = (
            f'/api/reservations/{reservation_id}/status/'
        )

        response = self.client.post(
            status_url,
            {
                'status': 'confirmed',
                'reason': 'تلاش کاربر ناشناس'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_update_reservation_status_invalid_status(self):
        permission = Permission.objects.get(
            codename='can_change_reservation_status'
        )

        self.user.user_permissions.add(
            permission
        )

        self.client.force_authenticate(
            user=self.user
        )

        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        status_url = (
            f'/api/reservations/{reservation_id}/status/'
        )

        response = self.client.post(
            status_url,
            {
                'status': 'invalid_status',
                'reason': 'وضعیت نامعتبر برای تست'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_update_reservation_status_not_found(self):
        permission = Permission.objects.get(
            codename='can_change_reservation_status'
        )

        self.user.user_permissions.add(
            permission
        )

        self.client.force_authenticate(
            user=self.user
        )

        status_url = (
            '/api/reservations/999999/status/'
        )

        response = self.client.post(
            status_url,
            {
                'status': 'confirmed',
                'reason': 'تست رزرو ناموجود'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_reservation_history_multiple_status_changes(self):
        permission = Permission.objects.get(
            codename='can_change_reservation_status'
        )

        view_permission = Permission.objects.get(
            codename='can_view_all_reservations'
        )

        self.user.user_permissions.add(
            permission,
            view_permission
        )

        self.client.force_authenticate(
            user=self.user
        )

        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        status_url = (
            f'/api/reservations/{reservation_id}/status/'
        )

        response = self.client.post(
            status_url,
            {
                'status': 'confirmed',
                'reason': 'تایید رزرو'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        response = self.client.post(
            status_url,
            {
                'status': 'cancelled',
                'reason': 'لغو رزرو'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        history_url = (
            f'/api/reservations/{reservation_id}/history/'
        )

        response = self.client.get(
            history_url
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            2
        )

        self.assertEqual(
            response.data[0]['old_status'],
            'pending'
        )

        self.assertEqual(
            response.data[0]['new_status'],
            'confirmed'
        )

        self.assertEqual(
            response.data[1]['old_status'],
            'confirmed'
        )

        self.assertEqual(
            response.data[1]['new_status'],
            'cancelled'
        )

    def test_invalid_transition_does_not_create_history(
            self
    ):
        permission = Permission.objects.get(
            codename='can_change_reservation_status'
        )

        self.user.user_permissions.add(
            permission
        )

        self.client.force_authenticate(
            user=self.user
        )

        create_url = (
            f'/api/devices/{self.device.id}/reservations/'
        )

        create_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        create_response = self.client.post(
            create_url,
            create_data,
            format='json'
        )

        self.assertEqual(
            create_response.status_code,
            201
        )

        reservation_id = create_response.data['id']

        status_url = (
            f'/api/reservations/{reservation_id}/status/'
        )

        # pending → confirmed
        response = self.client.post(
            status_url,
            {
                'status': 'confirmed',
                'reason': 'تایید رزرو'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        reservation = Reservation.objects.get(
            id=reservation_id
        )

        self.assertEqual(
            reservation.history.count(),
            1
        )

        # confirmed → confirmed
        response = self.client.post(
            status_url,
            {
                'status': 'confirmed',
                'reason': 'تلاش برای انتقال نامعتبر'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            400
        )

        reservation.refresh_from_db()

        self.assertEqual(
            reservation.status,
            'confirmed'
        )

        self.assertEqual(
            reservation.history.count(),
            1
        )