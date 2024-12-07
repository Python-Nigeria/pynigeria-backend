from rest_framework.test import APITransactionTestCase
from .models import User, OTPCode
from django.urls import reverse
from django.utils import timezone
from django.core import mail


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
