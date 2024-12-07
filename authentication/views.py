from rest_framework.views import APIView
from .serializers import (
    RegisterSerializer,
    ValidationError,
    IntegrityError,
    EmailVerifyBeginSerializer,
    EmailVerifyCompleteSerializer,
)
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import Throttled
from drf_spectacular.utils import extend_schema


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    throttle_classes = [AnonRateThrottle]

    @extend_schema(operation_id="v1_register", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_user_data = serializer.save()
            response_data = self.serializer_class(new_user_data).data
            return Response({"data": response_data}, status=status.HTTP_201_CREATED)


class VerifyEmailBeginView(APIView):
    """
    This view exists to initialize email verification manually if the auto option fails.
    """
    serializer_class = EmailVerifyBeginSerializer
    throttle_classes = [AnonRateThrottle]

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

    @extend_schema(operation_id="v1_verify_email_complete", tags=["auth_v1"])
    def post(self, request, token):
        serializer = self.serializer_class(data={}, context={"token": token})
        if serializer.is_valid(raise_exception=True):
            user_data = serializer.save()
            response_data = self.serializer_class(user_data).data
            return Response({"data": response_data}, status=status.HTTP_200_OK)
