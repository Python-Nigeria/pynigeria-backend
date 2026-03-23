from django.db.models import Q
from django.db.transaction import atomic
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.filterset import JobFilterset
from common.helper import Helper

from .email import JobNotificationEmail
from .models import Bookmark, BookmarkFolder, Job
from .permissions import IsJobPoster, HasObjectPermission
from .serializers import (
    BookmarkFolderSerializer,
    BookmarkSerializer,
    JobApproveSerializer,
    JobSerializer,
)

# Create your views here.


class JobViewset(viewsets.ModelViewSet, Helper):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsJobPoster]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        "job_title",
        "employment_type",
        "tags__name",
    ]
    ordering_fields = [
        "job_title",
        "employment_type",
        "tags__name",
        "salary",
    ]
    ordering = ["job_title"]
    filterset_class = JobFilterset
    lookup_field = "slug"

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed(method="get")

    def filter_queryset(self, queryset):
        """
        Apply additional search filters while maintaining queryset ordering.
        """
        search_param = self.request.query_params.get("search")

        if search_param:
            search_terms = [
                term.strip().lower() for term in search_param.split(",") if term.strip()
            ]
            skill_filter = Q()
            for term in search_terms:
                skill_filter |= (
                    Q(job_title__icontains=term)
                    | Q(employment_type__icontains=term)
                    | Q(tags__name__icontains=term)
                    | Q(job_skills__skill_level__icontains=term)
                )
            queryset = queryset.filter(skill_filter).distinct()

        return super().filter_queryset(queryset)

    @atomic()
    def create(self, request, *args, **kwargs):
        slug = self.generate_slug()
        posted_by = self.request.user if self.request.user.is_authenticated else ""

        serializer = self.get_serializer(
            data=request.data,
            context={
                "request": request,
                "slug": slug,
                "posted_by": posted_by,
            },
        )
        serializer.is_valid(raise_exception=True)
        created_instance = serializer.create(serializer.validated_data)
        response_data = self.get_serializer(
            created_instance, context={"request": request}
        ).data

        return Response(response_data, status=201)

    @action(
        methods=["get"],
        detail=False,
        url_path="job-list",
        url_name="job-list",
    )
    def job_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @atomic()
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.update(instance, serializer.validated_data)
        response_data = self.get_serializer(
            updated_instance, context={"request": request}
        ).data
        return Response(response_data)

    @atomic()
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @atomic()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)


class JobApproveView(APIView):
    serializer_class = JobApproveSerializer
    permission_classes = [IsAdminUser]

    @atomic()
    def post(self, request, slug):

        job_instance = Job.objects.get(slug=slug)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_job = serializer.save(job_instance=job_instance)
        status = "approved" if updated_job.is_approved else "rejected"
        message = (
            serializer.data.get("message") if serializer.data.get("message") else None
        )

        JobNotificationEmail(updated_job).send_to_poster(
            updated_job.is_approved, message
        )
        return Response(
            {
                "status": status.title(),
                "message": message,
                "is_approved": updated_job.is_approved,
            },
            status=200,
        )


class BookmarkFolderViewset(viewsets.ModelViewSet):
    queryset = BookmarkFolder.objects.all().order_by("-created_at")
    serializer_class = BookmarkFolderSerializer
    permission_classes = [HasObjectPermission]

    def get_queryset(self):
        if self.action == "list" or self.action == "retrieve":
            return BookmarkFolder.objects.filter(user=self.request.user)
        else:
            return self.serializer_class

    @atomic()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        folder_instance = serializer.create(serializer.validated_data)
        response_data = self.get_serializer(
            folder_instance, context={"request": request}
        ).data
        return Response(response_data)

    @atomic()
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.update(instance, serializer.validated_data)
        response_data = self.get_serializer(
            updated_instance, context={"request": request}
        ).data
        return Response(response_data)

    @atomic()
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @atomic()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)


class BookmarkViewset(viewsets.ModelViewSet):
    queryset = Bookmark.objects.all()
    permission_classes = [HasObjectPermission]
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    @atomic()
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @atomic()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @atomic()
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.update(instance, serializer.validated_data)
        response_data = self.get_serializer(
            updated_instance, context={"request": request}
        ).data
        return Response(response_data)

    @atomic()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        bookmark_instance = serializer.create(serializer.validated_data)
        response_data = self.get_serializer(
            bookmark_instance, context={"request": request}
        ).data
        return Response(response_data)
