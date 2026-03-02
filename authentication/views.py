from io import BytesIO

import qrcode
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.renderers import BaseRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from social_core.actions import do_auth
from social_django.utils import psa

from .serializers import (
    EmailVerifyBeginSerializer,
    EmailVerifyCompleteSerializer,
    LoginSerializer,
    QRCodeDataSerializer,
    RegisterSerializer,
    TOTPDeviceCreateSerializer,
    VerifyTOTPDeviceSerializer,
)
from .social_authentication import complete_social_authentication
from django.middleware.csrf import get_token
from rest_framework.permissions import AllowAny


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_register", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_user_data = serializer.save()
            response_data = self.serializer_class(new_user_data).data
            return Response({"data": response_data}, status=status.HTTP_201_CREATED)
            

class VerifyEmailBeginView(APIView):
    """
    This view exists to initiate email verification manually if the auto option fails.
    """

    serializer_class = EmailVerifyBeginSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_verify_email_begin", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_data = serializer.save()
            response_data = self.serializer_class(user_data).data
            return Response({"data": response_data}, status=status.HTTP_200_OK)


class VerifyEmailCompleteView(APIView):
    serializer_class = EmailVerifyCompleteSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_verify_email_complete", tags=["auth_v1"])
    def post(self, request, token):
        serializer = self.serializer_class(data={}, context={"token": token})
        if serializer.is_valid(raise_exception=True):
            user_data = serializer.save()
            response_data = self.serializer_class(user_data).data
            return Response({"data": response_data}, status=status.HTTP_200_OK)


class TOTPDeviceCreateView(APIView):
    serializer_class = TOTPDeviceCreateSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_create_totp_device", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            device_data = serializer.save()
            response_data = self.serializer_class(device_data).data
            return Response({"data": response_data}, status=status.HTTP_201_CREATED)


class GetQRCodeView(APIView):
    serializer_class = QRCodeDataSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    class PNGRenderer(BaseRenderer):
        media_type = "image/png"
        format = "png"
        charset = None
        render_style = "binary"

        def render(self, data, accepted_media_type=None, renderer_context=None):
            return data

    @extend_schema(operation_id="v1_get_qrcode", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
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
        """
        This method defines renderers for both image and text.
        PNGRenderer is used when the response contains the QR code.
        BrowsableAPIRenderer is in case of error messages, compatible with DRF's browsable API.
        """
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
    serializer_class = VerifyTOTPDeviceSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_verify_totp_device", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            device_data = serializer.save()
            response_data = self.serializer_class(device_data).data
            return Response({"data": response_data}, status=status.HTTP_200_OK)


class LoginView(APIView):
    serializer_class = LoginSerializer
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="v1_login", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_data = serializer.save()
            response_data = self.serializer_class(user_data).data
            return Response({"data": response_data}, status=status.HTTP_200_OK)


@method_decorator(
    [csrf_exempt, never_cache, psa("authentication:social-complete")], name="get"
)
class SocialAuthenticationBeginView(APIView):
    """This view initiates social oauth authentication"""

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
    """This view completes social oauth authentication"""

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

class CsrfTokenView(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        #Genrate and get CSRF token
        csrf_token = get_token(request)
        return Response(dict(csrfToken=csrf_token))