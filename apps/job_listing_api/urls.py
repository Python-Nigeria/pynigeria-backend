from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    BookmarkFolderViewset,
    BookmarkViewset,
    JobApproveView,
    JobViewset,
)

app_name = "job_posting_v1"

router = DefaultRouter()

router.register(r"job", JobViewset,basename="job")
router.register(r"bookmark", BookmarkViewset)
router.register(r"bookmark-folders", BookmarkFolderViewset)


urlpatterns = [
    path("", include(router.urls)),
    path("job/approve/<slug:slug>/", JobApproveView.as_view(), name="job-approve"),
    path("login/", TokenObtainPairView.as_view()),
]
