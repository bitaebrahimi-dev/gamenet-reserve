from django.test import TestCase
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm
from .services import register_user
from django.contrib.auth.hashers import check_password
from .models import Profile
from django.urls import reverse
from django.db import IntegrityError


class AccountTestCase(TestCase):

    def test_successful_user_registration(self):
        form_data = {
            'username': 'testuser',
            'password1': 'StrongPass12345',
            'password2': 'StrongPass12345',
        }

        form = RegisterForm(form_data)

        self.assertTrue(
            form.is_valid()
        )

        user = register_user(form)

        self.assertIsNotNone(
            user
        )

        self.assertTrue(
            User.objects.filter(
                username='testuser'
            ).exists()
        )

    def test_registration_with_different_passwords(self):
        form_data = {
            'username': 'testuser2',
            'password1': 'StrongPass12345',
            'password2': 'DifferentPass12345',
        }

        form = RegisterForm(form_data)

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            'password2',
            form.errors
        )

        self.assertFalse(
            User.objects.filter(
                username='testuser2'
            ).exists()
        )

    def test_password_is_hashed_after_registration(self):
        form_data = {
            'username': 'testuser3',
            'password1': 'StrongPass12345',
            'password2': 'StrongPass12345',
        }

        form = RegisterForm(form_data)

        self.assertTrue(
            form.is_valid()
        )

        user = register_user(form)

        self.assertNotEqual(
            user.password,
            'StrongPass12345'
        )

        self.assertTrue(
            check_password(
                'StrongPass12345',
                user.password
            )
        )

    def test_profile_created_after_user_registration(self):
        form_data = {
            'username': 'profileuser',
            'password1': 'StrongPass12345',
            'password2': 'StrongPass12345',
        }

        form = RegisterForm(form_data)

        self.assertTrue(
            form.is_valid()
        )

        user = register_user(form)

        self.assertTrue(
            hasattr(user, 'profile')
        )

        self.assertEqual(
            user.profile.user,
            user
        )

    def test_default_role_for_new_user_profile(self):
        form_data = {
            'username': 'roleuser',
            'password1': 'StrongPass12345',
            'password2': 'StrongPass12345',
        }

        form = RegisterForm(form_data)

        self.assertTrue(
            form.is_valid()
        )

        user = register_user(form)

        self.assertEqual(
            user.profile.role,
            'CUSTOMER'
        )

    def test_successful_login(self):
        user = User.objects.create_user(
            username='loginuser',
            password='StrongPass12345'
        )

        form = LoginForm(
            data={
                'username': 'loginuser',
                'password': 'StrongPass12345',
            }
        )

        self.assertTrue(
            form.is_valid()
        )

        authenticated_user = form.get_user()

        self.assertEqual(
            authenticated_user,
            user
        )

    def test_login_with_wrong_password(self):
        user = User.objects.create_user(
            username='wrongpassuser',
            password='StrongPass12345'
        )

        form = LoginForm(
            data={
                'username': 'wrongpassuser',
                'password': 'WrongPassword12345',
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIsNone(
            form.get_user()
        )

    def test_successful_logout(self):
        user = User.objects.create_user(
            username='logoutuser',
            password='StrongPass12345'
        )

        self.client.login(
            username='logoutuser',
            password='StrongPass12345'
        )

        response = self.client.get(
            reverse('logout')
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )

    def test_profile_deleted_when_user_is_deleted(self):
        user = User.objects.create_user(
            username='deleteuser',
            password='StrongPass12345'
        )

        profile = user.profile

        self.assertTrue(
            Profile.objects.filter(
                user=user
            ).exists()
        )

        user.delete()

        self.assertFalse(
            Profile.objects.filter(
                id=profile.id
            ).exists()
        )

    def test_user_cannot_have_multiple_profiles(self):
        user = User.objects.create_user(
            username='multipleprofileuser',
            password='StrongPass12345'
        )

        self.assertTrue(
            Profile.objects.filter(
                user=user
            ).exists()
        )

        with self.assertRaises(
                IntegrityError
        ):
            Profile.objects.create(
                user=user
            )
