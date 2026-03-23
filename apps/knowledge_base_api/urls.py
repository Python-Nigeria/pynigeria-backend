from django.urls import path

from . import views

app_name = "knowledge_base_api_v1"


urlpatterns = [
    # Methods:
    # GET : List all the user uploads,
    # POST : Create a new user upload
    path(
        "api/uploads/",
        views.UserUploadListCreateViewAPIView.as_view(),
        name="user_upload_list_create",
    ),
    # Methods:
    # GET : Retrieve a user upload using ID,
    # PUT : Update a user upload using ID,
    # DELETE : Delete a user upload
    path(
        "api/uploads/<int:pk>/",
        views.UserUploadDetailAPIView.as_view(),
        name="user_upload_detail",
    ),
    # Methods:
    # GET : List all published uploads with status 'APPROVED',
    path(
        "api/uploads/published/",
        views.PublishedUploadsListAPIView.as_view(),
        name="approved_uploads_list",
    ),
    # Methods:
    # PATCH : Update the status of a user upload (PENDING -> APPROVED or REJECTED)
    # note: (only available to admin users)
    path(
        "api/uploads/<int:pk>/status/",
        views.UpdateUploadStatusAPIView.as_view(),
        name="update_upload_status",
    ),
    # Methods:
    # GET : List all the uploads of an authenticated user
    path(
        "api/uploads/mine/",
        views.UserUploadsListAPIView.as_view(),
        name="user_uploads_list",
    ),
]
