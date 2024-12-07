from django.urls import path
from .views import RegisterView, VerifyEmailBeginView, VerifyEmailCompleteView


app_name = "authentication"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/begin/", VerifyEmailBeginView.as_view(), name="verify-email-begin"),
    path("verify-email/complete/<str:token>/", VerifyEmailCompleteView.as_view(), name="verify-email-complete"),
]