from io import BytesIO

import qrcode
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import BaseRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from social_core.actions import do_auth
from social_django.utils import psa

from .serializers import (
    EmailVerifyBeginSerializer,
    EmailVerifyCompleteSerializer,
    LoginSerializer,
    LoginTOTPSerializer,  # new — Step 2 of login
    QRCodeDataSerializer,
    RegisterSerializer,
    TOTPDeviceCreateSerializer,
    VerifyTOTPDeviceSerializer,
)
from .social_authentication import complete_social_authentication

# ─── Registration ─────────────────────────────────────────────────────────────


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_register", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(
                {"data": self.serializer_class(user).data},
                status=status.HTTP_201_CREATED,
            )


# ─── Email Verification ───────────────────────────────────────────────────────


class VerifyEmailBeginView(APIView):
    """Resend verification email if the original link was missed or expired."""

    serializer_class = EmailVerifyBeginSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_verify_email_begin", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            return Response(
                {"data": self.serializer_class(result).data},
                status=status.HTTP_200_OK,
            )


class VerifyEmailCompleteView(APIView):
    serializer_class = EmailVerifyCompleteSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_verify_email_complete", tags=["auth_v1"])
    def post(self, request):
        token = request.query_params.get("token")
        serializer = self.serializer_class(data=request.data, context={"token": token})
        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            return Response(
                {"data": result},
                status=status.HTTP_200_OK,
            )


# ─── Login ────────────────────────────────────────────────────────────────────


class LoginView(APIView):
    """
    Step 1 — validates email + password.
    Returns tokens immediately if 2FA is off.
    Returns { requires_2fa: true, email } if 2FA is on, so the frontend
    knows to show the TOTP prompt and call LoginTOTPView next.
    """

    serializer_class = LoginSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_login", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            return Response({"data": result}, status=status.HTTP_200_OK)


class LoginTOTPView(APIView):
    """
    Step 2 — only called when LoginView returned requires_2fa=True.
    Accepts the 6-digit TOTP code and returns tokens if valid.
    """

    serializer_class = LoginTOTPSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_login_totp", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            return Response({"data": result}, status=status.HTTP_200_OK)


# ─── Optional 2FA Setup (authenticated users only) ───────────────────────────


class TOTPDeviceCreateView(APIView):
    """
    Creates an unconfirmed TOTP device for the logged-in user.
    Requires authentication — 2FA setup lives in settings, not during signup.
    """

    serializer_class = TOTPDeviceCreateSerializer
    throttle_classes = [UserRateThrottle]  # authenticated throttle, not anon
    permission_classes = [IsAuthenticated]  # must be logged in

    @extend_schema(operation_id="v1_create_totp_device", tags=["auth_v1"])
    def post(self, request):
        # Pass request in context so the serializer can get request.user
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            device = serializer.save()
            return Response(
                {
                    "data": self.serializer_class(
                        device, context={"request": request}
                    ).data
                },
                status=status.HTTP_201_CREATED,
            )


class GetQRCodeView(APIView):
    """
    Returns a PNG QR code image for the user's unconfirmed TOTP device.
    Requires authentication.
    """

    serializer_class = QRCodeDataSerializer
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated]

    class PNGRenderer(BaseRenderer):
        media_type = "image/png"
        format = "png"
        charset = None
        render_style = "binary"

        def render(self, data, accepted_media_type=None, renderer_context=None):
            return data

    @extend_schema(operation_id="v1_get_qrcode", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            otpauth_url = serializer.save()
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(otpauth_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color=(0, 0, 0), back_color=(255, 255, 255))
            image_buffer = BytesIO()
            img.save(image_buffer)
            image_buffer.seek(0)
            return Response(
                image_buffer.getvalue(),
                content_type="image/png",
                status=status.HTTP_200_OK,
            )

    def finalize_response(self, request, response, *args, **kwargs):
        if response.content_type == "image/png":
            response.accepted_renderer = GetQRCodeView.PNGRenderer()
            response.accepted_media_type = GetQRCodeView.PNGRenderer.media_type
            response.renderer_context = {}
        else:
            response.accepted_renderer = BrowsableAPIRenderer()
            response.accepted_media_type = BrowsableAPIRenderer.media_type
            response.renderer_context = {
                "response": response.data,
                "view": self,
                "request": request,
            }
        for key, value in self.headers.items():
            response[key] = value
        return response


class VerifyTOTPDeviceView(APIView):
    """
    Confirms the TOTP device after the user scans the QR and enters their first code.
    Requires authentication.
    """

    serializer_class = VerifyTOTPDeviceSerializer
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="v1_verify_totp_device", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            device = serializer.save()
            return Response(
                {
                    "data": self.serializer_class(
                        device, context={"request": request}
                    ).data
                },
                status=status.HTTP_200_OK,
            )


# ─── Social Auth ──────────────────────────────────────────────────────────────


@method_decorator(
    [csrf_exempt, never_cache, psa("authentication:social-complete")], name="get"
)
class SocialAuthenticationBeginView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="v1_social_auth_begin",
        tags=["auth_v1"],
        request=None,
        responses=None,
    )
    def get(self, request, backend):
        return do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)


@method_decorator(
    [csrf_exempt, never_cache, psa("authentication:social-complete")], name="get"
)
class SocialAuthenticationCompleteView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="v1_social_auth_complete",
        tags=["auth_v1"],
        request=None,
        responses=None,
    )
    def get(self, request, backend):
        return complete_social_authentication(request, backend)


# ─── CSRF ─────────────────────────────────────────────────────────────────────


class CsrfTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_csrf_token", tags=["auth_v1"])
    def get(self, request):
        return Response({"csrfToken": get_token(request)})
