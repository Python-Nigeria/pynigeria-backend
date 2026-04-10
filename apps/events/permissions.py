from rest_framework import permissions


class IsEventOwnerOrAdminDelete(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if request.method in permissions.SAFE_METHODS:
			return True

		if request.method == "DELETE":
			return obj.created_by == request.user or request.user.is_staff

		return obj.created_by == request.user
