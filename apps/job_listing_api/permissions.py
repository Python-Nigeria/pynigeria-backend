from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsJobPoster(BasePermission):

    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True
        if view.action == "job_list":
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        if request.method in ["DELETE", "PUT", "PATCH"]:
            return obj.posted_by == request.user or request.user.is_staff
        return False

class HasObjectPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        if request.method in ["DELETE", "PUT", "PATCH"]:
            return obj.user == request.user or request.user.is_staff
        return False