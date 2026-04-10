import random
from config.settings.development import *
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core import signing

from .models import OTPVerification


class EmailOTP:
    """
    Generates a signed OTP verification link and sends it to the user's email.
    Called manually from serializers — not via signal — since we need
    to control exactly when the email fires (e.g. on resend, on expiry).
    """

    def __init__(self, user, context="signup"):
        self.user = user
        self.user_id = str(user.id)
        self.user_email = user.email
        self.context = context
        self.code = str(random.randint(100000, 999999))

        # Signed token for magic links (remains for signup/convenience)
        self.signed_token = signing.dumps(
            obj=(self.code, self.user_id),
            key=settings.SECRET_KEY,
        )

        # This should point to your frontend verify page, not the API endpoint
        origin = settings.CURRENT_ORIGIN.rstrip("/")
        self.verification_url = f"{origin}/verify-email/{self.signed_token}"

        if self.context == "login":
            self.subject = "Your Python 9ja login code"
        else:
            self.subject = "Verify your email – Python 9ja"

    def send_email(self):
        # The frontend page then calls the API with the token

        if self.context == "login":
            text_fallback = (
                f"Hi,\n\nYour login verification code is {self.code}.\n\n"
                f"This code expires in 10 minutes.\n\n"
                f"If you didn't request this, ignore this email."
            )
        else:
            text_fallback = (
                f"Hi,\n\nVerify your Python 9ja account by visiting:\n{self.verification_url}\n\n"
                f"This link expires in 10 minutes.\n\nIf you didn't create this account, ignore this email."
            )

        html_message = self._build_html(self.verification_url)

        # EmailMultiAlternatives sends both plain text and HTML
        # Plain text is the fallback for email clients that don't render HTML
        email = EmailMultiAlternatives(
            subject=self.subject,
            body=text_fallback,
            from_email=f"Python 9ja <{settings.SENDER_EMAIL}>",
            to=[self.user_email],
        )
        email.attach_alternative(html_message, "text/html")

        try:
            email.send(fail_silently=False)
            # Only create the OTP record after the email actually sends successfully
            # Delete any old code first to avoid unique constraint issues on resend
            OTPVerification.objects.filter(user=self.user, is_used=False).delete()
            OTPVerification.objects.create(otp=self.code, user=self.user)
        except Exception as e:
            raise Exception(f"Failed to send verification email: {e}")

    def _build_html(self, verification_url):
        is_login = self.context == "login"
        title = (
            "Login Verification – Python 9ja"
            if is_login
            else "Verify your email – Python 9ja"
        )
        headline = "Login Security Code 🔐" if is_login else "Welcome to Python 9ja! 🎉"

        if is_login:
            body_content = f"""
              <p style="margin:0 0 16px;font-size:15px;color:#4b5563;line-height:1.7;">
                To complete your login, please enter the following 6-digit code:
              </p>
              <table cellpadding="0" cellspacing="0" width="100%" style="margin:24px 0;">
                <tr>
                  <td align="center">
                    <div style="background:#f3f4f6;border-radius:12px;padding:20px 40px;display:inline-block;letter-spacing:10px;">
                      <span style="font-family:monospace;font-size:36px;font-weight:bold;color:#111827;">{self.code}</span>
                    </div>
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 16px;font-size:15px;color:#4b5563;line-height:1.7;">
                Do not share this code with anyone.
              </p>
            """
        else:
            feature_list = "".join(
                f"""
                <tr>
                  <td style="padding:6px 0;">
                    <table cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="font-size:16px;padding-right:10px;">{icon}</td>
                        <td style="font-size:14px;color:#374151;">{text}</td>
                      </tr>
                    </table>
                  </td>
                </tr>"""
                for icon, text in [
                    ("💼", "120+ Python job listings updated weekly"),
                    ("📰", "Curated Nigerian tech news every week"),
                    ("🤝", "Project collaborations &amp; mentorship"),
                    ("💬", "Community forums &amp; developer discussions"),
                ]
            )
            body_content = f"""
              <p style="margin:0 0 16px;font-size:15px;color:#4b5563;line-height:1.7;">
                You're one step away from joining <strong>2,400+ Python developers</strong>
                across Nigeria. Verify your email to unlock your full account.
              </p>
              <p style="margin:0 0 28px;font-size:15px;color:#4b5563;line-height:1.7;">
                Once verified, you'll get access to:
              </p>
              <table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:32px;">
                {feature_list}
              </table>
              <table cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td align="center">
                    <a href="{verification_url}"
                       style="display:inline-block;background:linear-gradient(135deg,#059669,#10b981);
                              color:#ffffff;font-size:15px;font-weight:700;text-decoration:none;
                              padding:14px 36px;border-radius:10px;letter-spacing:0.3px;">
                      ✅ Verify My Email
                    </a>
                  </td>
                </tr>
              </table>
            """

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f7f6;font-family:'Segoe UI',Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f7f6;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="100%" cellpadding="0" cellspacing="0"
               style="max-width:560px;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.06);">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#065f46 0%,#10b981 100%);padding:36px 40px;text-align:center;">
              <h1 style="margin:0;font-size:26px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">
                🐍 Python<span style="color:#6ee7b7;">9ja</span>
              </h1>
              <p style="margin:8px 0 0;font-size:13px;color:#a7f3d0;letter-spacing:0.5px;">
                Nigeria's Python Developer Community
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 40px 32px;">
              <h2 style="margin:0 0 12px;font-size:22px;font-weight:700;color:#111827;">
                {headline}
              </h2>
              {body_content}
              <!-- Expiry notice -->
              <p style="margin:24px 0 0;font-size:13px;color:#9ca3af;text-align:center;line-height:1.6;">
                ⏱ This code/link expires in <strong>10 minutes</strong>.
              </p>
            </td>
          </tr>

          <!-- Fallback URL -->
          <tr>
            <td style="padding:0 40px 24px;">
              <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:14px 16px;">
                <p style="margin:0 0 6px;font-size:12px;color:#6b7280;font-weight:600;">
                  Button not working? Copy and paste this link:
                </p>
                <p style="margin:0;font-size:11px;color:#059669;word-break:break-all;">
                  {verification_url}
                </p>
              </div>
            </td>
          </tr>

          <!-- Security notice -->
          <tr>
            <td style="padding:0 40px 32px;">
              <p style="margin:0;font-size:12px;color:#9ca3af;line-height:1.6;">
                🔒 If you didn't create a Python 9ja account, you can safely ignore this email.
                Someone may have entered your email address by mistake.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f9fafb;border-top:1px solid #e5e7eb;padding:20px 40px;text-align:center;">
              <p style="margin:0;font-size:12px;color:#9ca3af;">
                © {
            settings.CURRENT_YEAR if hasattr(settings, "CURRENT_YEAR") else "2025"
        } Python 9ja · Made with ❤️ in Nigeria 🇳🇬
              </p>
              <p style="margin:6px 0 0;font-size:12px;color:#9ca3af;">
                You're receiving this because you signed up at
                <a href="{
            settings.CURRENT_ORIGIN
        }" style="color:#059669;text-decoration:none;">
                  python9ja.com
                </a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""
