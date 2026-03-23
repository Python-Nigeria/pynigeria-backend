from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserUpload
from .permissions import CustomPermission
from .serializers import UserUploadSerializer

# Create your views here.


class UserUploadListCreateViewAPIView(generics.ListCreateAPIView):
    queryset = UserUpload.objects.all()
    serializer_class = UserUploadSerializer
    permission_classes = [CustomPermission]
    ordering_fields = ["created_at", "published_at"]

    def perform_create(self, serializer):
        """
        Associates the authenticated user with the UserUpload instance
        being created and saves it to the database.
        """
        serializer.save(user=self.request.user)


class UserUploadDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserUpload.objects.all()
    serializer_class = UserUploadSerializer
    permission_classes = [CustomPermission]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class PublishedUploadsListAPIView(generics.ListAPIView):
    queryset = UserUpload.published.all()
    serializer_class = UserUploadSerializer
    permission_classes = [CustomPermission]


class UpdateUploadStatusAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        upload = get_object_or_404(UserUpload, pk=pk)
        new_status = request.data.get("status")
        try:
            upload.update_file_status(new_status)
            return Response(
                {"status": "success", "message": "Status updated successfully."}
            )
        except ValidationError as e:
            return Response({"status": "error", "message": str(e)}, status=400)


class UserUploadsListAPIView(generics.ListAPIView):
    serializer_class = UserUploadSerializer
    permission_classes = [CustomPermission]

    def get_queryset(self):
        return UserUpload.objects.filter(user=self.request.user)
