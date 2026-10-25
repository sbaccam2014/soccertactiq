from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()

SIGNUP_URL = "/_allauth/browser/v1/auth/signup"
LOGIN_URL = "/_allauth/browser/v1/auth/login"
LOGOUT_URL = "/_allauth/browser/v1/auth/session"
ME_URL = "/api/auth/me/"


class RegistrationLoginLogoutTests(APITestCase):
    """
    Covers the brief's acceptance criteria: "Registration/login/logout
    and case-insensitive username uniqueness."
    """

    def _get_csrf(self):
        # allauth's session GET establishes the csrftoken cookie, exactly
        # as the SPA does on load.
        self.client.get(LOGOUT_URL)
        return self.client.cookies["csrftoken"].value

    def test_registration_creates_user_and_player_profile(self):
        csrf = self._get_csrf()
        response = self.client.post(
            SIGNUP_URL,
            {"username": "newplayer", "password": "StrongPass123!"},
            HTTP_X_CSRFTOKEN=csrf,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username="newplayer")
        self.assertTrue(hasattr(user, "player_profile"))
        # Permanent ID is the primary key — never username/email.
        self.assertIsInstance(user.pk, int)

    def test_registration_rejects_case_insensitive_duplicate(self):
        User.objects.create_user(username="TakenName", password="StrongPass123!")

        csrf = self._get_csrf()
        response = self.client.post(
            SIGNUP_URL,
            {"username": "takenname", "password": "AnotherPass123!"},
            HTTP_X_CSRFTOKEN=csrf,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.filter(username__iexact="takenname").count(), 1)

    def test_login_then_logout_then_me_requires_auth(self):
        User.objects.create_user(username="loginuser", password="StrongPass123!")
        csrf = self._get_csrf()

        login_response = self.client.post(
            LOGIN_URL,
            {"username": "loginuser", "password": "StrongPass123!"},
            HTTP_X_CSRFTOKEN=csrf,
            content_type="application/json",
        )
        self.assertEqual(login_response.status_code, 200)

        me_response = self.client.get(ME_URL)
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()["username"], "loginuser")

        csrf2 = self.client.cookies["csrftoken"].value
        logout_response = self.client.delete(LOGOUT_URL, HTTP_X_CSRFTOKEN=csrf2)
        # allauth's documented convention: logout's result is the new
        # (unauthenticated) session state, returned as 401.
        self.assertEqual(logout_response.status_code, 401)

        me_after_logout = self.client.get(ME_URL)
        self.assertIn(me_after_logout.status_code, (401, 403))

    def test_login_with_wrong_password_fails(self):
        User.objects.create_user(username="realuser", password="StrongPass123!")
        csrf = self._get_csrf()
        response = self.client.post(
            LOGIN_URL,
            {"username": "realuser", "password": "WrongPassword!"},
            HTTP_X_CSRFTOKEN=csrf,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_is_case_insensitive_for_username(self):
        User.objects.create_user(username="CaseUser", password="StrongPass123!")
        csrf = self._get_csrf()
        response = self.client.post(
            LOGIN_URL,
            {"username": "caseuser", "password": "StrongPass123!"},
            HTTP_X_CSRFTOKEN=csrf,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_anonymous_cannot_read_current_user(self):
        response = self.client.get(ME_URL)
        self.assertIn(response.status_code, (401, 403))


class UserModelConstraintTests(APITestCase):
    def test_db_level_case_insensitive_uniqueness(self):
        from django.db import IntegrityError, transaction

        User.objects.create_user(username="dbuser", password="x")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(username="DBUser", password="y")

    def test_admin_form_rejects_case_insensitive_duplicate(self):
        from accounts.forms import BsaUserCreationForm

        User.objects.create_user(username="formuser", password="x")
        form = BsaUserCreationForm(
            data={
                "username": "FormUser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
