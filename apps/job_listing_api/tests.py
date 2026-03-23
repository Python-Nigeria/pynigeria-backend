from django.urls import reverse
from rest_framework.test import APITransactionTestCase
from rest_framework_simplejwt.tokens import AccessToken

from authentication.models import User

from .models import Job


class JobAddingTestCase(APITransactionTestCase):
    def setUp(self):
        self.job_path = reverse("job-list")

        # Create a test user and generate a token
        self.user = User.objects.create_user(
            email="test@gmail.com", password="password123", is_superuser=True
        )
        self.token = str(
            AccessToken.for_user(self.user)
        )  # Generate JWT token for the test user

    def test_adding_success(self):
        # Add the Authorization header with the Bearer token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.post(
            self.job_path,
            data={
                "title": "Software Developer",
                "company": "Tech Solutions Inc.",
                "description": "We are looking for a skilled software developer to join our team. The ideal candidate will have experience with Python, JavaScript, and web development frameworks.",
                "location": "New York, USA",
                "employment_type": "Full Time",
                "skills": [
                    {"name": "Python"},
                    {"name": "JavaScript"},
                    {"name": "Django"},
                    {"name": "React"},
                    {"name": "SQL"},
                ],
                "salary": 200000,
                "application_deadline": "2024-12-31",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        for field in {"id", "title", "posted_by"}:
            self.assertTrue(field in response.data)


# class JobUpdateTestCase(APITransactionTestCase):
#     def setUp(self):
#         # Create a test user and generate a token
#         self.user = User.objects.create_user(email="test@gmail.com", password="password123", is_superuser=True)
#         self.token = str(AccessToken.for_user(self.user))  # Generate JWT token for the test user
#         self.job = JobPosting.objects.create(title="Software Developer",
#                 company_name="Tech Solutions Inc.",
#                 description="We are looking for a skilled software developer to join our team. The ideal candidate will have experience with Python, JavaScript, and web development frameworks.",
#                 location= "New York, USA",
#                 job_type= "FT",
#                 skills_required= "Python, JavaScript, Django, React, SQL",
#                 last_date_to_apply="2024-12-31T23:59:59Z",
#                 is_active=False) # create one job posting for testing
#         self.update_path = reverse("job:job_posting_upate", kwargs={'pk': self.job.pk})


#     def test_update_job(self):
#         # Add the Authorization header with the Bearer token
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
#         response = self.client.put(
#             self.update_path, data= {
#                 "title": "Python Developer",
#                 "company_name": "Tech Solutions Inc.",
#                 "description": "We are looking for a skilled software developer to join our team. The ideal candidate will have experience with Python, JavaScript, and web development frameworks.",
#                 "location": "New York, USA",
#                 "job_type": "PT",
#                 "skills_required": "Python, JavaScript, Django, React, SQL",
#                 "last_date_to_apply": "2024-12-31T23:59:59Z",
#                 "is_active": False
#                 }
#         )
#         self.assertEqual(
#             response.data["title"], "Python Developer"
#         )
#         self.assertEqual(
#             response.data["job_type"], "PT"
#         )

# class JobDeleteTestCase(APITransactionTestCase):
#     def setUp(self):
#         # Create a test user and generate a token
#         self.user = User.objects.create_user(email="test@gmail.com", password="password123", is_superuser=True)
#         self.token = str(AccessToken.for_user(self.user))  # Generate JWT token for the test user
#         self.job = JobPosting.objects.create(title="Software Developer",
#                 company_name="Tech Solutions Inc.",
#                 description="We are looking for a skilled software developer to join our team. The ideal candidate will have experience with Python, JavaScript, and web development frameworks.",
#                 location= "New York, USA",
#                 job_type= "FT",
#                 skills_required= "Python, JavaScript, Django, React, SQL",
#                 last_date_to_apply="2024-12-31T23:59:59Z",
#                 is_active=False) # create one job posting for testing
#         self.delete_path = reverse("job:job_posting_delete", kwargs={'pk': self.job.pk})


#     def test_delete_job(self):
#         # Add the Authorization header with the Bearer token
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
#         response = self.client.delete(
#             self.delete_path
#         )
#         self.assertEqual(
#             response.data["message"], "Job posting deleted successfully"
#         )


# class JobListTestCase(APITransactionTestCase):
#     def setUp(self):
#         # Create a test user and generate a token to post job. though not need to view the jobs
#         self.user = User.objects.create_user(email="test@gmail.com", password="password123", is_superuser=True)
#         self.token = str(AccessToken.for_user(self.user))  # Generate JWT token for the test user
#         self.job = JobPosting.objects.create(title="Software Developer",
#                 company_name="Tech Solutions Inc.",
#                 description="We are looking for a skilled software developer to join our team. The ideal candidate will have experience with Python, JavaScript, and web development frameworks.",
#                 location= "New York, USA",
#                 job_type= "FT",
#                 skills_required= "Python, JavaScript, Django, React, SQL",
#                 last_date_to_apply="2024-12-31T23:59:59Z",
#                 is_active=False) # create one job posting for testing
#         self.list_path = reverse("job:job_posting_list",)


#     def test_list_job(self):
#         # No credentials needed to view jobs
#         response = self.client.get(
#             self.list_path
#         )
#         # check that the list returned is not empty
#         self.assertNotEqual(
#             response.data[0], []
#         )


# class JobDetailTestCase(APITransactionTestCase):
#     def setUp(self):
#         # Create a test user and generate a token
#         self.user = User.objects.create_user(email="test@gmail.com", password="password123", is_superuser=True)
#         self.token = str(AccessToken.for_user(self.user))  # Generate JWT token for the test user
#         self.job = JobPosting.objects.create(title="Software Developer",
#                 company_name="Tech Solutions Inc.",
#                 description="We are looking for a skilled software developer to join our team. The ideal candidate will have experience with Python, JavaScript, and web development frameworks.",
#                 location= "New York, USA",
#                 job_type= "FT",
#                 skills_required= "Python, JavaScript, Django, React, SQL",
#                 last_date_to_apply="2024-12-31T23:59:59Z",
#                 is_active=False) # create one job posting for testing
#         self.detail_path = reverse("job:job_posting_detail", kwargs={'slug': self.job.slug})


#     def test_job_detail(self):
#         # Add the Authorization header with the Bearer token
#         response = self.client.get(
#             self.detail_path
#         )
#         for field in {"id", "title", "slug"}:
#             self.assertTrue(field in response.data)
