from time import sleep

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
            self.register_path, data={"email": "test1@gmail.com"}
        )
        for field in {"id", "email", "message"}:
            self.assertTrue(field in response.data["data"])
        self.assertEqual(response.data["data"]["is_email_verified"], False)

        user = User.objects.filter(email="test1@gmail.com").first()
        self.assertTrue(user.is_otp_email_sent)
        # Test for sent email
        self.assertIsNotNone(mail.outbox[0].body.split("'")[1].split("/")[7])

    def test_register_integrity_failure(self):
        response = self.client.post(
            self.register_path, data={"email": "test@gmail.com"}
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
            "Check your email for a verification link.",
        )
        self.assertIsNotNone(self.user.otp.code)
        self.assertIsNotNone(mail.outbox[0].body.split("'")[1].split("/")[7])

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
            "Check your email for an already existing verification link.",
        )
        self.assertIsNotNone(mail.outbox[0].body.split("'")[1].split("/")[7])

    def tearDown(self):
        User.objects.all().delete()
        OTPCode.objects.all().delete()
        mail.outbox.clear()


class VerifyEmailCompleteTestCase(APITransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@gmail.com")
        self.verification_token = mail.outbox[0].body.split("'")[1].split("/")[7]

    def test_verify_email_complete_success(self):
        response = self.client.post(
            reverse(
                "authentication:verify-email-complete",
                kwargs={"token": self.verification_token},
            ),
            data={},
        )
        self.assertEqual(
            response.data["data"]["message"],
            "Your email has been verified successfully. Proceed to 2FA setup.",
        )
        response2 = self.client.post(
            reverse(
                "authentication:verify-email-complete",
                kwargs={"token": self.verification_token},
            ),
            data={},
        )
        self.assertEqual(response2.data["detail"], "Otp code does not exist.")

    def test_verify_email_complete_invalid_code_failure(self):
        response = self.client.post(
            reverse(
                "authentication:verify-email-complete",
                kwargs={"token": self.verification_token + "n"},
            ),
            data={},
        )
        self.assertEqual(response.data["detail"], "Invalid otp code detected.")

    def test_verify_email_complete_expired_failure(self):
        user2 = User.objects.create_user(email="test2@gmail.com")
        otp = OTPCode.objects.filter(user=user2).first()
        otp.expiry = timezone.now() - timezone.timedelta(minutes=15)
        otp.save()
        verification_token2 = mail.outbox[1].body.split("'")[1].split("/")[7]
        response = self.client.post(
            reverse(
                "authentication:verify-email-complete",
                kwargs={"token": verification_token2},
            ),
            data={},
        )
        self.assertEqual(
            response.data["detail"],
            "Otp code has expired. a new verification link has been sent to your email.",
        )
        self.assertIsNotNone(mail.outbox[2].body.split("'")[1].split("/")[7])

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

    def test_create_device_success(self):
        response = self.client.post(self.device_create, data={"email": self.user.email})
        for item in {"user", "name", "confirmed"}:
            self.assertIn(item, response.data["data"])
        self.assertFalse(response.data["data"]["confirmed"])

        response2 = self.client.post(
            self.device_create, data={"email": self.user.email}
        )
        self.assertEqual(
            response2.data["detail"], "A totp device already exists for this account."
        )

    def test_create_device_failure_unverified_email(self):
        self.user.is_email_verified = False
        self.user.save()
        response = self.client.post(self.device_create, data={"email": self.user.email})
        self.assertEqual(
            response.data["detail"],
            "This account has not been verified. check your email for a verification link or request a new one.",
        )

    def test_create_device_failure_nonexisting_user(self):
        response = self.client.post(
            self.device_create, data={"email": "test@gmail.none"}
        )
        self.assertEqual(
            response.data["detail"],
            "No existing account is associated with this email.",
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
            "No unconfirmed totp device is associated with this email.",
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
        self.assertEqual(response.data["detail"], "Invalid totp token detected.")

    def tearDown(self):
        User.objects.all().delete()
        TOTPDevice.objects.all().delete()


class LoginTestCase(APITransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="admin@gmail.com", is_email_verified=True
        )
        self.otp_device = TOTPDevice.objects.create(
            user=self.user, name=self.user.email, confirmed=True
        )
        self.login = reverse("authentication:login")

    def test_login_success(self):
        self.user.is_2fa_enabled = True
        self.user.save()
        otp_code = TOTP(self.otp_device.bin_key).token()
        response = self.client.post(
            self.login, data={"email": self.user.email, "otp_code": otp_code}
        )
        self.assertIn("access", response.data["data"])
        self.assertEqual(response.status_code, 200)

    def test_login_failure_no_account(self):
        self.user.is_2fa_enabled = True
        self.user.save()
        otp_code = TOTP(self.otp_device.bin_key).token()
        response = self.client.post(
            self.login, data={"email": "admi1n@gmail.com", "otp_code": otp_code}
        )
        self.assertEqual(
            response.data["detail"], "No account is associated with this email."
        )

    def test_login_failure_2fa_not_set(self):
        response = self.client.post(
            self.login, data={"email": self.user.email, "otp_code": 386267}
        )
        self.assertEqual(
            response.data["detail"], "2FA setup must be completed before login."
        )

    def test_login_failure_no_totp_device(self):
        self.user.is_2fa_enabled = True
        self.user.save()
        self.otp_device.delete()
        response = self.client.post(
            self.login, data={"email": self.user.email, "otp_code": 638387}
        )
        self.assertEqual(
            response.data["detail"],
            "No confirmed totp device is associated with this email.",
        )

    def tearDown(self):
        return super().tearDown()
