from django.conf import settings
from django.db import models
from django.conf import settings
# from django.contrib.auth.models import User
# Create your models here.


class UserActivity(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='activity', on_delete=models.CASCADE,null=True,blank=True)
	whatsapp_number = models.IntegerField(null=True,blank=True)
	status = models.BooleanField(default=True)

	def __init__(self):
		return f"{self.user} Activity"




class Message(models.Model):
	user = models.ForeignKey(
			UserActivity, on_delete=models.CASCADE, related_name="messages"
	)
	title = models.CharField(max_length=10000, default="This Month")
	total_message = models.IntegerField(default=0)

	def __init__(self):
		return f"{self.user.user} Messages"