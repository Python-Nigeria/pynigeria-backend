from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission


class CustomPermission(BasePermission):

    def has_permission(self, request, view):
        User = get_user_model()
        return request.user and request.user.is_authenticated
