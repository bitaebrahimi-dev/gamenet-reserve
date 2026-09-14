from django.test import TestCase
from django.contrib.auth.models import User
from devices.models import Device
from .forms import ReservationForm
from datetime import date, time, timedelta
from .services import (
    create_reservation,
    cancel_reservation_by_customer,
    update_reservation_status
)
from .models import Reservation, ReservationHistory
from django.core.exceptions import ValidationError


class ReservationTestCase(TestCase):
    pass

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password'
        )
        self.device = Device.objects.create(
            name='Test PS5',
            is_active=True,
            device_type='PS5',
            hourly_price=100000
        )

    def test_create_reservation_success(self):
        form_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }
        form = ReservationForm(form_data)
        self.assertTrue(form.is_valid())
        reservation = create_reservation(
            form=form,
            user=self.user,
            device=self.device
        )
        self.assertEqual(
            Reservation.objects.count(),
            1
        )
        self.assertEqual(
            reservation.user,
            self.user
        )
        self.assertEqual(
            reservation.status,
            'pending'
        )

    def test_create_reservation_with_past_date(self):
        past_date = date.today() - timedelta(days=1)
        form_data = {
            'reservation_date': past_date,
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }
        form = ReservationForm(form_data)
        with self.assertRaises(ValidationError):
            create_reservation(
                form=form,
                user=self.user,
                device=self.device
            )

    def test_create_reservation_with_invalid_time(self):
        form_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(16, 0),
            'end_time': time(14, 0),
        }
        form = ReservationForm(form_data)
        with self.assertRaises(ValidationError):
            create_reservation(
                form=form,
                user=self.user,
                device=self.device
            )

    def test_create_reservation_with_inactive_device(self):
        inactive_device = Device.objects.create(
            name='Inactive PS5',
            device_type='PS5',
            hourly_price=100000,
            is_active=False
        )
        form_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }
        form = ReservationForm(form_data)
        self.assertTrue(form.is_valid())
        with self.assertRaises(ValidationError):
            create_reservation(
                form=form,
                user=self.user,
                device=inactive_device
            )

    def test_create_reservation_with_time_conflict(self):
        first_form_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }
        first_form = ReservationForm(first_form_data)
        self.assertTrue(first_form.is_valid())
        create_reservation(
            form=first_form,
            user=self.user,
            device=self.device
        )
        second_form_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(15, 0),
            'end_time': time(17, 0),
        }
        second_form = ReservationForm(second_form_data)
        self.assertTrue(second_form.is_valid())
        with self.assertRaises(ValidationError):
            create_reservation(
                form=second_form,
                user=self.user,
                device=self.device
            )

    def test_customer_can_cancel_own_reservation(self):
        form_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }
        form = ReservationForm(form_data)
        self.assertTrue(form.is_valid())
        reservation = create_reservation(
            form=form,
            user=self.user,
            device=self.device
        )
        cancel_reservation_by_customer(
            reservation=reservation,
            user=self.user
        )
        reservation.refresh_from_db()
        self.assertEqual(
            reservation.status,
            'cancelled'
        )
        self.assertEqual(
            reservation.history.count(),
            1
        )
        history = reservation.history.first()

        self.assertEqual(
            history.old_status,
            'pending'
        )

        self.assertEqual(
            history.new_status,
            'cancelled'
        )

        self.assertEqual(
            history.changed_by,
            self.user
        )

    def test_customer_cannot_cancel_other_users_reservation(self):
        other_user = User.objects.create_user(
            username='other_user',
            password='12345678'
        )
        form_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }
        form = ReservationForm(form_data)
        self.assertTrue(form.is_valid())
        reservation = create_reservation(
            form=form,
            user=self.user,
            device=self.device
        )
        with self.assertRaises(ValidationError):
            cancel_reservation_by_customer(
                reservation=reservation,
                user=other_user
            )

    def test_manager_can_confirm_reservation(self):
        manager = User.objects.create_user(
            username='manager',
            password='12345678'
        )
        form_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        form = ReservationForm(form_data)

        self.assertTrue(form.is_valid())

        reservation = create_reservation(
            form=form,
            user=self.user,
            device=self.device
        )

        update_reservation_status(
            reservation=reservation,
            status='confirmed',
            user=manager,
            reason='تایید توسط مدیر'
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

        history = reservation.history.first()

        self.assertEqual(
            history.old_status,
            'pending'
        )

        self.assertEqual(
            history.new_status,
            'confirmed'
        )

        self.assertEqual(
            history.changed_by,
            manager
        )

    def test_cannot_confirm_cancelled_reservation(self):
        manager = User.objects.create_user(
            username='manager2',
            password='12345678'
        )

        form_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        form = ReservationForm(form_data)

        self.assertTrue(form.is_valid())

        reservation = create_reservation(
            form=form,
            user=self.user,
            device=self.device
        )

        cancel_reservation_by_customer(
            reservation=reservation,
            user=self.user
        )

        reservation.refresh_from_db()

        self.assertEqual(
            reservation.status,
            'cancelled'
        )

        with self.assertRaises(ValidationError):
            update_reservation_status(
                reservation=reservation,
                status='confirmed',
                user=manager,
                reason='تلاش برای تایید رزرو لغو شده'
            )

    def test_customer_cannot_cancel_confirmed_reservation(self):
        manager = User.objects.create_user(
            username='manager3',
            password='12345678'
        )

        form_data = {
            'reservation_date': date.today() + timedelta(days=1),
            'start_time': time(14, 0),
            'end_time': time(16, 0),
        }

        form = ReservationForm(form_data)

        self.assertTrue(form.is_valid())

        reservation = create_reservation(
            form=form,
            user=self.user,
            device=self.device
        )

        update_reservation_status(
            reservation=reservation,
            status='confirmed',
            user=manager,
            reason='تایید توسط مدیر'
        )

        reservation.refresh_from_db()

        self.assertEqual(
            reservation.status,
            'confirmed'
        )

        with self.assertRaises(ValidationError):
            cancel_reservation_by_customer(
                reservation=reservation,
                user=self.user
            )