import pytest
from django.urls import reverse
from django.core import mail

from allauth.account.models import EmailConfirmationHMAC
from allauth.account.forms import EmailAwarePasswordResetTokenGenerator
from dj_rest_auth.utils import jwt_encode

from users.models import User


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestSignupView:
    url = reverse("signup")

    def test_signup(self, api_client, user_built):
        user_data = {
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "password1": user_built.password,
            "password2": user_built.password,
        }
        response = api_client.post(self.url, user_data, format="json")

        assert response.status_code == 201
        assert response.json() == {"detail": "Verification e-mail sent."}

        email = mail.outbox[0]
        self.email_sent = email
        assert email.to == [user_data["email"]]
        assert "Please Confirm Your Email Address" in email.subject

        assert User.objects.count() == 1

        user = User.objects.first()
        expected_data = {**user_data}
        expected_data.pop("password1")
        expected_data.pop("password2")

        assert all(getattr(user, field) == user_data[field] for field in expected_data)
        assert user.check_password(user_data["password1"])

    def test_signup_failed(self, api_client):
        user_data = {}
        response = api_client.post(self.url, user_data, format="json")

        assert response.status_code == 400
        assert response.data != {}


class TestVerifyEmailView:
    url = reverse("rest_verify_email")

    def test_verify_email(self, api_client, create_user_with_email_address):
        user_data = create_user_with_email_address(verified=False)
        email_address = user_data["user_created"].emailaddress_set.first()
        email_confirmation = EmailConfirmationHMAC.create(email_address)

        data = {"key": email_confirmation.key}
        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 200

    def test_verify_email_with_invalid_code(self, api_client):
        data = {"key": "this is invalid key"}
        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 404

    def test_verify_email_with_bad_data(self, api_client):
        data = {}
        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 400
        assert set(response.json().keys()) == {"key"}


class TestResendEmailView:
    url = reverse("rest_resend_email")

    def test_resend_email_to_unverified_account(
        self, api_client, create_user_with_email_address
    ):
        user_data = create_user_with_email_address(verified=False)
        user = user_data["user_created"]

        data = {"email": user.email}
        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 200

        email = mail.outbox[0]
        self.email_sent = email
        assert email.to == [user.email]
        assert "Please Confirm Your Email Address" in email.subject

    def test_resend_email_to_verified_account(
        self, api_client, create_user_with_email_address
    ):
        user_data = create_user_with_email_address(verified=True)
        user = user_data["user_created"]

        data = {"email": user.email}
        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 200
        assert len(mail.outbox) == 0

    def test_resend_email_to_unregistered_account(self, api_client):
        target_email = "test@test.com"
        data = {"email": target_email}
        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 200
        assert len(mail.outbox) == 0

    def test_resend_email_fails_with_bad_data(self, api_client):
        data = {}
        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 400
        assert set(response.json().keys()) == {"email"}


class TestLoginView:
    url = reverse("rest_login")

    def test_login_successful(self, api_client, create_user_with):
        user_password = "super_secure_password"
        user_created = create_user_with(password=user_password)
        User.objects.setup_user_email(user_created, verified=True)

        credentials = {"email": user_created.email, "password": user_password}
        response = api_client.post(self.url, credentials, format="json")

        assert response.status_code == 200
        assert set(response.data.keys()) == {
            "access",
            "refresh",
            "access_expiration",
            "refresh_expiration",
            "user",
        }
        assert response.data["user"] == {
            "id": str(user_created.id),
            "email": user_created.email,
            "first_name": user_created.first_name,
            "last_name": user_created.last_name,
        }

    def test_login_fails_with_unverified_email(self, api_client, create_user_with):
        user_password = "super_secure_password"
        user_created = create_user_with(password=user_password)
        User.objects.setup_user_email(user_created, verified=False)

        credentials = {"email": user_created.email, "password": user_password}
        response = api_client.post(self.url, credentials, format="json")

        assert response.status_code == 400
        assert "non_field_errors" in response.json()
        assert response.json()["non_field_errors"][0] == "E-mail is not verified."

    def test_login_fails_with_invalid_credentials(self, api_client, create_user_with):
        user_password = "super_secure_password"
        user_created = create_user_with(password=user_password)
        User.objects.setup_user_email(user_created, verified=True)

        credentials = {"email": user_created.email, "password": "invalid_password"}
        response = api_client.post(self.url, credentials, format="json")

        assert response.status_code == 400
        assert "non_field_errors" in response.json()
        assert (
            response.json()["non_field_errors"][0]
            == "Unable to log in with provided credentials."
        )

    def test_login_fails_with_bad_data(self, api_client, create_user_with):
        user_password = "super_secure_password"
        user_created = create_user_with(password=user_password)
        User.objects.setup_user_email(user_created, verified=True)

        credentials = {}
        response = api_client.post(self.url, credentials, format="json")

        assert response.status_code == 400
        assert set(response.json().keys()) == {"email", "password"}


class ParentTokenView:
    @pytest.fixture(autouse=True)
    def set_access_and_refres_tokens(self, create_user_with_email_address):
        user_data = create_user_with_email_address()
        user = user_data["user_created"]
        access_token, refresh_token = jwt_encode(user)

        self.user = user
        self.user_dict = user_data["user_created_dict"]
        self.access_token = str(access_token)
        self.refresh_token = str(refresh_token)


class TestTokenRefreshView(ParentTokenView):
    url = reverse("token_refresh")

    def test_refresh_token(self, api_client):
        refresh_data = {"refresh": self.refresh_token}

        response = api_client.post(self.url, refresh_data, format="json")

        assert response.status_code == 200
        assert set(response.data.keys()) == {
            "access",
            "refresh",
            "access_expiration",
            "refresh_expiration",
        }

    def test_refresh_token_failed_with_bad_data(self, api_client):
        refresh_data = {}
        response = api_client.post(self.url, refresh_data, format="json")

        assert response.status_code == 401

    def test_refresh_token_failed_with_invalid_token(self, api_client):
        refresh_data = {"refresh": "invalid token"}
        response = api_client.post(self.url, refresh_data, format="json")

        assert response.status_code == 401


class TestTokenVerifyView(ParentTokenView):
    url = reverse("token_verify")

    def test_verify_token(self, api_client):
        token_data = {"token": self.access_token}
        response = api_client.post(self.url, token_data, format="json")

        assert response.status_code == 200

    def test_verify_token_failed_with_bad_data(self, api_client):
        token_data = {}
        response = api_client.post(self.url, token_data, format="json")

        assert response.status_code == 400
        assert set(response.data.keys()) == {"token"}

    def test_verify_token_failed_with_invalid_token(self, api_client):
        token_data = {"token": "invalid token"}
        response = api_client.post(self.url, token_data, format="json")

        assert response.status_code == 401


class TestLoggedInUser:
    url = reverse("rest_user_details")

    def test_retrieve_user_details(self, api_client, create_user_with_email_address):
        user_data = create_user_with_email_address()
        user_instance = user_data["user_created"]
        user_dict = user_data["user_created_dict"]

        api_client.force_authenticate(user_instance)
        response = api_client.get(self.url, format="json")

        assert response.status_code == 200
        assert response.json() == user_dict

    def test_unauthenticated_user_cannot_retrieve_details(self, api_client):
        response = api_client.get(self.url, format="json")
        assert response.status_code == 401


class TestPasswordChange:
    url = reverse("rest_password_change")

    def test_change_password_successful(
        self, api_client, create_user_with_email_address
    ):
        user = create_user_with_email_address()["user_created"]

        passwords = {
            "new_password1": "ThisIsNewPassword",
            "new_password2": "ThisIsNewPassword",
        }
        api_client.force_authenticate(user)
        response = api_client.post(self.url, passwords, format="json")

        assert response.status_code == 200
        assert response.json()["detail"] == "New password has been saved."

    def test_change_password_fails_with_bad_data(
        self, api_client, create_user_with_email_address
    ):
        user = create_user_with_email_address()["user_created"]

        passwords = {}
        api_client.force_authenticate(user)
        response = api_client.post(self.url, passwords, format="json")

        assert response.status_code == 400
        assert set(response.json().keys()) == {"new_password1", "new_password2"}

    def test_unauthenticated_user_cannot_change_password(self, api_client):
        passwords = {
            "new_password1": "ThisIsNewPassword",
            "new_password2": "ThisIsNewPassword",
        }
        response = api_client.post(self.url, passwords, format="json")

        assert response.status_code == 401


class TestPasswordReset:
    url = reverse("rest_password_reset")

    def test_reset_password_of_a_verified_account(
        self, api_client, create_user_with_email_address
    ):
        user = create_user_with_email_address(verified=True)["user_created"]

        data = {"email": user.email}
        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 200

        email = mail.outbox[0]
        assert email.to == [user.email]
        assert "Password Reset Email" in email.subject

    def test_reset_password_to_unregistered_account(self, api_client):
        data = {"email": "test@test.com"}
        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 200

        email = mail.outbox[0]
        assert email.to == [data["email"]]
        assert "Unknown Account" in email.subject


class TestPasswordResetConfirm:
    url = reverse("rest_password_reset_confirm")

    def test_password_reset_confirm(self, api_client, create_user_with_email_address):
        user = create_user_with_email_address()["user_created"]
        token_generator = EmailAwarePasswordResetTokenGenerator()
        token = token_generator.make_token(user)

        data = {
            "new_password1": "NewPasswordTest",
            "new_password2": "NewPasswordTest",
            "uid": str(user.id),
            "token": token,
        }
        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 200
        assert (
            response.json()["detail"]
            == "Password has been reset with the new password."
        )

    def test_password_reset_confirm_fails_with_bad_data(self, api_client):
        data = {}
        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 400
        assert set(response.json().keys()) == {
            "new_password1",
            "new_password2",
            "uid",
            "token",
        }
