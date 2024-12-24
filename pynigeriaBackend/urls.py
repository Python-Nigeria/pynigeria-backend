"""
URL configuration for pynigeriaBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from job_listing_api.views import JobViewset, BookmarkViewset
from django.conf.urls.static import static
from django.conf import settings

router = DefaultRouter()

router.register(r"job", JobViewset)
router.register(r"bookmark", BookmarkViewset, "bookmark")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path(
        "api/v1/authentication/",
        include("authentication.urls", namespace="authentication_v1"),
    ),
    path("api/v1/jobs/", include("job.urls", namespace="job_posting_v1")),
    path(
      "api/v1/knowledge-base/",
      include("knowledge_base_api.urls", namespace="knowledge_base_api_v1"),
    ),
    # Schema and documentation below
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)