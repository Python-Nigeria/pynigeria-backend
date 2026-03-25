import re
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTP, TOTPDevice
from rest_framework.test import APITransactionTestCase

from .models import OTPCode, User

"""
RUN COMMAND:
python3 manage.py test --settings=authentication.test_settings authentication
"""


class RegisterTestCase(APITransactionTestCase):
    def setUp(self):
        self.register_path = reverse("authentication:register")
        User.objects.create_user(email="test@gmail.com", is_test_user=True)

    def test_register_success(self):
        response = self.client.post(
            self.register_path,
            data={"email": "test1@gmail.com", "password": "password123"},
        )
        for field in {"id", "email", "message"}:
            self.assertTrue(field in response.data["data"])
        self.assertEqual(response.data["data"]["is_email_verified"], False)

        user = User.objects.filter(email="test1@gmail.com").first()
        # Test for sent email
        self.assertIsNotNone(
            re.search(r"token=([^&\s\"' >]+)", mail.outbox[0].body).group(1)
        )

    def test_register_and_verify_success(self):
        # 1. Register
        response = self.client.post(
            self.register_path,
            data={"email": "newuser@gmail.com", "password": "password123"},
        )
        self.assertEqual(response.status_code, 201)

        # 2. Extract token from mail
        verification_token = re.search(
            r"token=([^&\s\"' >]+)", mail.outbox[0].body
        ).group(1)

        # 3. Verify
        response2 = self.client.post(
            f"{reverse('authentication:verify-email-complete')}?token={verification_token}",
            data={},
        )
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(
            response2.data["data"]["message"],
            "Email verified successfully. You are now logged in.",
        )
        self.assertIn("access", response2.data["data"])

        # 4. Check user status
        user = User.objects.get(email="newuser@gmail.com")
        self.assertTrue(user.is_email_verified)

    def test_register_integrity_failure(self):
        response = self.client.post(
            self.register_path,
            data={"email": "test@gmail.com", "password": "password123"},
        )
        self.assertEqual(
            response.data["detail"], "An account with this email already exists."
        )

    def tearDown(self):
        User.objects.all().delete()
        mail.outbox.clear()


class VerifyEmailBeginTestCase(APITransactionTestCase):
    def setUp(self):
        self.verify_begin_path = reverse("authentication:verify-email-begin")
        self.user = User.objects.create_user(email="test@gmail.com", is_test_user=True)

    def test_verify_email_begin_success(self):
        response = self.client.post(
            self.verify_begin_path, data={"email": self.user.email}
        )
        self.assertEqual(
            response.data["data"]["message"],
            "Check your email for a verification code/link.",
        )
        self.assertIsNotNone(self.user.otp.code)
        self.assertIsNotNone(
            re.search(r"token=([^&\s\"' >]+)", mail.outbox[0].body).group(1)
        )

    def test_verify_email_begin_missing_field_failure(self):
        response = self.client.post(self.verify_begin_path, data={})
        self.assertEqual(response.data["detail"], "Email field is required.")

    def test_verify_email_begin_non_existing_user_failure(self):
        response = self.client.post(
            self.verify_begin_path, data={"email": "test2@gmail.com"}
        )
        self.assertEqual(
            response.data["detail"],
            "No existing account is associated with this email.",
        )

    def test_verify_email_begin_existing_otp_failure(self):
        self.user2 = User.objects.create_user(
            email="test2@gmail.com", is_test_user=True
        )
        self.client.post(self.verify_begin_path, data={"email": self.user2.email})
        response = self.client.post(
            self.verify_begin_path, data={"email": self.user2.email}
        )
        self.assertEqual(
            response.data["detail"],
            "A verification link/code was already sent. check your email.",
        )
        self.assertIsNotNone(
            re.search(r"token=([^&\s\"' >]+)", mail.outbox[0].body).group(1)
        )

    def tearDown(self):
        User.objects.all().delete()
        OTPCode.objects.all().delete()
        mail.outbox.clear()


class VerifyEmailCompleteTestCase(APITransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@gmail.com")
        self.verification_token = re.search(
            r"token=([^&\s\"' >]+)", mail.outbox[0].body
        ).group(1)

    def test_verify_email_complete_success(self):
        response = self.client.post(
            f"{reverse('authentication:verify-email-complete')}?token={self.verification_token}",
            data={},
        )
        self.assertEqual(
            response.data["data"]["message"],
            "Email verified successfully. You are now logged in.",
        )
        response2 = self.client.post(
            f"{reverse('authentication:verify-email-complete')}?token={self.verification_token}",
            data={},
        )
        self.assertEqual(
            response2.data["detail"], "Otp code does not exist or is invalid."
        )

    def test_verify_email_complete_invalid_code_failure(self):
        response = self.client.post(
            f"{reverse('authentication:verify-email-complete')}?token={self.verification_token}n",
            data={},
        )
        self.assertEqual(response.data["detail"], "Invalid verification token.")

    def test_verify_email_complete_expired_failure(self):
        user2 = User.objects.create_user(email="test2@gmail.com")
        otp = OTPCode.objects.filter(user=user2).first()
        otp.expiry = timezone.now() - timezone.timedelta(minutes=15)
        otp.save()
        verification_token2 = re.search(
            r"token=([^&\s\"' >]+)", mail.outbox[1].body
        ).group(1)
        response = self.client.post(
            f"{reverse('authentication:verify-email-complete')}?token={verification_token2}",
            data={},
        )
        self.assertEqual(
            response.data["detail"],
            "Link/code expired. a new verification code has been sent.",
        )
        self.assertIsNotNone(
            re.search(r"token=([^&\s\"' >]+)", mail.outbox[2].body).group(1)
        )

    def tearDown(self):
        User.objects.all().delete()
        OTPCode.objects.all().delete()
        mail.outbox.clear()


class TOTPCreateVerifyTestCase(APITransactionTestCase):
    def setUp(self):
        self.device_create = reverse("authentication:create-totp-device")
        self.user = User.objects.create_user(
            email="admin@gmail.com", is_email_verified=True
        )
        self.client.force_authenticate(user=self.user)

    def test_create_device_success(self):
        response = self.client.post(self.device_create, data={"email": self.user.email})
        for item in {"user", "name", "confirmed"}:
            self.assertIn(item, response.data["data"])
        self.assertFalse(response.data["data"]["confirmed"])

        response2 = self.client.post(
            self.device_create, data={"email": self.user.email}
        )
        self.assertEqual(response2.data["data"]["name"], self.user.email)

    def test_create_device_failure_unverified_email(self):
        self.user.is_email_verified = False
        self.user.save()
        response = self.client.post(self.device_create)
        self.assertEqual(
            response.data["detail"],
            "Please verify your email before enabling 2fa.",
        )

    def tearDown(self):
        User.objects.all().delete()
        TOTPDevice.objects.all().delete()


class GetQRCodeTestCase(APITransactionTestCase):
    def setUp(self):
        self.qrcode = reverse("authentication:get-qr-code")
        self.user = User.objects.create_user(
            email="admin@gmail.com", is_email_verified=True
        )
        self.client.force_authenticate(user=self.user)

    def test_get_qrcode_success(self):
        self.client.post(
            reverse("authentication:create-totp-device"),
            data={"email": self.user.email},
        )
        response = self.client.post(self.qrcode, data={"email": self.user.email})
        self.assertTrue(type(response.data) == bytes)

    def test_get_qrcode_failure(self):
        response = self.client.post(self.qrcode, data={"email": self.user.email})
        self.assertEqual(
            response.data["detail"],
            "No pending 2fa setup found. please start 2fa setup first.",
        )

    def tearDown(self):
        User.objects.all().delete()
        TOTPDevice.objects.all().delete()


class VerifyTOTPDeviceTestCase(APITransactionTestCase):
    def setUp(self):
        self.verify_device = reverse("authentication:verify-totp-device")
        self.user = User.objects.create_user(
            email="admin@gmail.com", is_email_verified=True
        )
        self.client.force_authenticate(user=self.user)

    def test_verify_totp_device_success(self):
        self.client.post(
            reverse("authentication:create-totp-device"),
            data={"email": self.user.email},
        )
        device = TOTPDevice.objects.filter(user=self.user).first()
        otp_token = TOTP(device.bin_key).token()
        response = self.client.post(
            self.verify_device,
            data={"email": self.user.email, "otp_token": otp_token},
        )
        for item in {"user", "name", "confirmed", "message"}:
            self.assertIn(item, response.data["data"])
        self.assertTrue(response.data["data"]["confirmed"])

    def test_verify_totp_device_failure_invalid_code(self):
        self.client.post(
            reverse("authentication:create-totp-device"),
            data={"email": self.user.email},
        )
        response = self.client.post(
            self.verify_device, data={"email": self.user.email, "otp_token": 123456}
        )
        self.assertEqual(response.data["detail"], "Invalid totp code. try again.")

    def tearDown(self):
        User.objects.all().delete()
        TOTPDevice.objects.all().delete()


class LoginTestCase(APITransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="admin@gmail.com", password="password123", is_email_verified=True
        )
        self.login = reverse("authentication:login")

    def test_login_success(self):
        # Step 1: Login leads to OTP email
        response = self.client.post(
            self.login, data={"email": self.user.email, "password": "password123"}
        )
        self.assertTrue(response.data["data"]["requires_email_otp"])
        self.assertEqual(response.status_code, 200)

        # Step 2: Verify OTP
        otp_code = OTPCode.objects.get(user=self.user).code
        response2 = self.client.post(
            reverse("authentication:verify-email-complete"),
            data={"email": self.user.email, "otp_code": otp_code},
        )
        self.assertEqual(response2.status_code, 200, f"Failed: {response2.data}")
        self.assertIn("access", response2.data["data"])

    def test_login_failure_no_account(self):
        response = self.client.post(
            self.login, data={"email": "admi1n@gmail.com", "password": "password123"}
        )
        self.assertEqual(
            response.data["detail"], "No account is associated with this email."
        )

    def test_login_failure_wrong_password(self):
        response = self.client.post(
            self.login, data={"email": self.user.email, "password": "wrongpassword"}
        )
        self.assertEqual(response.data["detail"], "Incorrect email or password.")

    def tearDown(self):
        return super().tearDown()
