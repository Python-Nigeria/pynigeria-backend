from django.contrib import admin
from .models import UserUpload


# Register your models here.


@admin.action(description='Approve selected uploads')
def approve_uploads(modeladmin, request, queryset):
  for upload in queryset:
    upload.update_status(UserUpload.Status.APPROVED)


@admin.action(description='Reject selected uploads')
def reject_uploads(modeladmin, request, queryset):
  for upload in queryset:
    upload.update_status(UserUpload.Status.REJECTED)


@admin.register(UserUpload)
class UserUploadAdmin(admin.ModelAdmin):
  list_display = ('user', 'upload_type', 'file', 'status', 'created_at')
  actions = [approve_uploads, reject_uploads]