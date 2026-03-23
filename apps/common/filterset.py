import django_filters

from job_listing_api.models import Job, JobTypeChoice


class JobFilterset(django_filters.FilterSet):
    job_title = django_filters.CharFilter(
        field_name="job_title",
        lookup_expr="icontains",
        label="Job Title"
    )
    tags__name = django_filters.CharFilter(
        field_name="tags__name",
        lookup_expr="icontains",
        label="Tag",
    )
    
    employment_type = django_filters.ChoiceFilter(choices=JobTypeChoice.choices, label="Job Type")

    class SalaryRangeFilter(django_filters.RangeFilter):
        def filter(self, qs, value):
            """
            Override the RangeFilter to convert salary range from naira to kobo.
            """
            if value:
                # Convert both bounds of the range from naira to kobo
                salary_min = value.start * 100 if value.start is not None else None
                salary_max = value.stop * 100 if value.stop is not None else None

                # Apply the range filter using the converted values
                if salary_min is not None and salary_max is not None:
                    return qs.filter(**{f"{self.field_name}__gte": salary_min, f"{self.field_name}__lte": salary_max})
                elif salary_min is not None:
                    return qs.filter(**{f"{self.field_name}__gte": salary_min})
                elif salary_max is not None:
                    return qs.filter(**{f"{self.field_name}__lte": salary_max})
            return qs
    salary = SalaryRangeFilter(field_name="salary")


    class Meta:
        model = Job
        fields = [
            "job_title",
            "tags__name",
            "employment_type",
            "salary"
        ]

    