from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.timezone import now
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from common.helper import Helper
from job_listing_api.models import (
    Bookmark,
    BookmarkFolder,
    Company,
    Job,
    JobSkill,
    JobTypeChoice,
    Skill,
)

User = get_user_model()


class SkillSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[], required=True)

    class Meta:
        model = Skill
        exclude = ("id",)


class JobSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer()
    skill_level = serializers.CharField(required=True)

    class Meta:
        model = JobSkill
        exclude = (
            "id",
            "job",
        )

    def to_internal_value(self, data):
        text_fields = ["skill_level"]
        for field in text_fields:
            if field in data and data[field]:
                data[field] = data[field].title()
        return super().to_internal_value(data)


class JobSerializer(TaggitSerializer, serializers.ModelSerializer, Helper):
    job = serializers.HyperlinkedIdentityField(
        view_name="job-detail", lookup_field="slug"
    )
    job_skills = JobSkillSerializer(many=True, required=True)
    tags = TagListSerializerField(read_only=True)
    employment_type = serializers.ChoiceField(choices=JobTypeChoice.choices)
    company_name = serializers.CharField(required=False)
    original_job = serializers.HyperlinkedRelatedField(
        view_name="job-detail", lookup_field="slug", read_only=True
    )

    class Meta:
        model = Job
        exclude = ("slug",)
        read_only_fields = [
            "posted_by",
            "created_at",
            "published_at",
            "views_count",
            "applications_count",
            "original_job",
            "status",
            "scheduled_publish_at",
            "is_approved",
            "version",
            # "tags",
        ]

    def to_internal_value(self, data):
        text_fields = ["employment_type", "status", "visibility"]
        for field in text_fields:
            if field in data and data[field]:
                data[field] = data[field].title()
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("id", None)
        data.pop("skills", None)
        # self._format_text_field(data)
        # self._format_list_fields(data)
        self._format_posted_by("posted_by", data)
        self._format_date_field(data)
        self._format_salary(data)

        return data

    def validate(self, attrs):
        if "salary" in attrs:
            attrs["salary"] = attrs["salary"] * 100

        for date_field in [
            "application_deadline",
            "published_at",
        ]:
            if date_field in attrs:
                date_value = attrs[date_field]
                if isinstance(date_value, datetime) and date_value.strftime(
                    "%Y-%m-%d"
                ) < now().strftime("%Y-%m-%d"):
                    raise ValidationError(
                        message={
                            date_field: f"{date_field.replace('_', ' ').capitalize()} cannot be in the past. "
                        },
                        code=400,
                    )
        for field in ["job_title", "job_description"]:
            if field in attrs and isinstance(attrs[field], str):
                attrs[field] = attrs[field].strip().lower()

        if "company" in attrs and attrs["company"] is not None:
            attrs["company"] = attrs.get("company")
            attrs["company_name"] = attrs.get("company").name.strip().lower()
        else:
            attrs["company"] = attrs.get("company")
            attrs["company_name"] = (
                attrs.get("company_name").strip().lower()
                if attrs.get("company_name")
                else None
            )
        job_skills = attrs.get("job_skills", [])
        if not job_skills:
            raise ValidationError({"job_skills": "Job skills cannot be empty."})

        for skill in job_skills:
            if not skill.get("skill"):
                raise ValidationError(
                    {"job_skills": "Each job skill must have a 'skill' field."}
                )
            if not skill.get("skill_level"):
                raise ValidationError(
                    {"job_skills": "Each job skill must have a 'skill_level' field."}
                )

        return super().validate(attrs)

    def create(self, validated_data):
        skills_data = validated_data.pop("job_skills", None)

        if "slug" not in validated_data:
            validated_data["slug"] = self.context.get("slug")
        if "posted_by" not in validated_data:
            validated_data["posted_by"] = self.context.get("posted_by")
        if "pubished_at" not in validated_data:
            validated_data["published_at"] = None

        with transaction.atomic():
            job_instance = Job.objects.create(**validated_data)

            for data in skills_data:
                skill_data = data["skill"]
                skill_instance, created = Skill.objects.get_or_create(
                    name=skill_data["name"].strip().lower()
                )

                # Create JobSkill instance and associate with Job
                JobSkill.objects.create(
                    job=job_instance,
                    skill=skill_instance,
                    skill_level=data["skill_level"],
                )
            if skills_data is not None:
                job_instance.tags.add(
                    *[data["skill"]["name"].strip().lower() for data in skills_data]
                )

        return job_instance

    def update(self, instance, validated_data):
        # Extract related fields from the validated data
        skills_data = validated_data.pop("job_skills", None)
        tags_data = validated_data.pop("tags", "[]")

        # Create a new instance as a copy of the current instance
        new_job_data = {
            field.name: getattr(instance, field.name)
            for field in instance._meta.fields
            if field.name not in ["id", "slug", "created_at"]
        }

        # Update new_job_data with validated_data
        new_job_data.update(validated_data)

        # Update the versioning details
        new_job_data["version"] = instance.version + 1
        new_job_data["original_job"] = instance
        new_job_data["slug"] = self.generate_slug()

        # Create the new job instance
        with transaction.atomic():

            new_instance = Job.objects.create(**new_job_data)

            # Update Many-to-Many fields (skills and tags)
            if skills_data is not None:
                skills_instances = []
                for items in skills_data:
                    if "skill" in items and items["skill"] is not None:
                        skill_instance, _ = Skill.objects.get_or_create(
                            name=items["skill"]["name"].strip().lower()
                        )
                    JobSkill.objects.get_or_create(
                        job=new_instance,
                        skill=skill_instance,
                        skill_level=items["skill_level"],
                    )
                    skills_instances.append(skill_instance)
                new_instance.skills.set(skills_instances)

            if skills_data is not None:
                new_instance.tags.add(
                    *[data["skill"]["name"].strip().lower() for data in skills_data]
                )

            new_instance.save()

        return new_instance


class JobApproveSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField()
    message = serializers.CharField(required=False)

    def save(self, job_instance, **kwargs):
        job_instance.is_approved = self.validated_data["is_approved"]
        job_instance.save()
        return job_instance


class BookmarkFolderSerializer(serializers.ModelSerializer, Helper):
    folder_instance = serializers.HyperlinkedIdentityField(
        view_name="bookmarkfolder-detail"
    )

    class Meta:
        model = BookmarkFolder
        exclude = ["created_at", "updated_at"]
        read_only_fields = ["user"]

    def validate(self, attrs):
        if "folder_name" in attrs:
            attrs["folder_name"] = attrs["folder_name"].strip().lower()
        if "folder_description" in attrs:
            attrs["folder_description"] = attrs["folder_description"].strip().lower()
        return super().validate(attrs)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("id", None)
        self._format_posted_by("user", data)
        self._format_date_field(data)
        # self._format_text_field(data)

        return data

    def create(self, validated_data: dict):

        if "user" not in validated_data:
            validated_data["user"] = self.context.get("request").user

        with transaction.atomic():
            folder_instance, created = BookmarkFolder.objects.get_or_create(
                **validated_data
            )
        return folder_instance

    def update(self, instance, validated_data:dict):
        with transaction.atomic():
            for attrs, value in validated_data.items():
                setattr(instance, attrs, value)
            instance.save()
        return instance


class BookmarkSerializer(serializers.ModelSerializer, Helper):
    bookmark = serializers.HyperlinkedIdentityField(view_name="bookmark-detail")
    job_instance = serializers.HyperlinkedRelatedField(
        view_name="job-detail", lookup_field="slug", source="job", read_only=True
    )

    class OverrideQuery(serializers.HyperlinkedRelatedField):

        def get_queryset(self):
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                return BookmarkFolder.objects.filter(user=request.user)
            return BookmarkFolder.objects.none()

    folder_instance = OverrideQuery(
        view_name="bookmarkfolder-detail",
        source="folder",
        lookup_field="pk",
        read_only=True,
    )

    class Meta:
        model = Bookmark
        exclude = ["created_at", "updated_at"]
        read_only_fields = ["user"]

    def validate(self, attrs):

        if "notes" in attrs and attrs["notes"]:
            attrs["notes"] = attrs["notes"].strip().lower()
        return super().validate(attrs)

    def create(self, validated_data: dict):

        if "user" not in validated_data:
            validated_data["user"] = self.context.get("request").user

        with transaction.atomic():
            bookmark_instance, created = Bookmark.objects.get_or_create(
                **validated_data
            )
        return bookmark_instance
    
    def update(self, instance, validated_data:dict):
        with transaction.atomic():
            for attrs, value in validated_data.items():
                setattr(instance, attrs, value)
            instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("id", None)
        self._format_posted_by("user", data)
        self._format_date_field(data)
        # self._format_text_field(data)
        # self._format_job_instance("job", data, self.context.get("request"))
        return data

    def to_internal_value(self, data):
        text_fields = ["status"]
        for field in text_fields:
            if field in data and data[field]:
                data[field] = data[field].title()
        return super().to_internal_value(data)


class CompanySerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[])

    class Meta:
        model = Company
        fields = "__all__"
