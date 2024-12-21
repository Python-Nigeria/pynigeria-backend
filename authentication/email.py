from .models import OTPCode
from pyotp import TOTP, random_base32
from django.core import signing
from django.conf import settings
from django.core.mail import send_mail


class EmailOTP:
    """
    This handles generation of OTP codes for email verification and sending of verification links to new users.
    The 'send_email' method is called through a signal when a new user object is saved.
    """

    def __init__(self, user):
        self.user = user
        self.code = None
        self.user_id = user.id
        self.user_email = user.email
        self.generate_otp()

    def generate_otp(self):
        self.code = TOTP(random_base32(), digits=6).now()

    def send_email(self):
        signed_token = signing.dumps(
            obj=(self.code, self.user_id), key=settings.SECRET_KEY
        )
        verification_url = f"{settings.CURRENT_ORIGIN}/api/v1/authentication/verify-email/{signed_token}"
        html_message = f"""
            <html>
                <body>
                    <p>
                        Click this link to verify your email:<br>
                        <a href='{verification_url}'>verification link</a>
                    </p>
                </body>
            </html>
        """
        subject = "Email Verification"
        try:
            mail_status = send_mail(
                subject=subject,
                message=html_message,
                from_email=settings.SENDER_EMAIL,
                recipient_list=[self.user_email],
                html_message=html_message,
                fail_silently=False,
            )
            if mail_status == 1:
                OTPCode.objects.create(code=self.code, user=self.user)
                self.user.is_otp_email_sent = True
                self.user.save()
        except Exception as e:
            raise Exception(str(e))
