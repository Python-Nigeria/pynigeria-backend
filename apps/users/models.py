from django.db import models
from django.contrib.auth import get_user_model


# Get the custom User model
User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=1000,blank=True,null=True)
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)
    github = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    experience_level = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100,blank=True)


    def __str__(self):
        return f"{self.username}'s Profile"