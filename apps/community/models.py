from django.db import models
from django.db.models import CASCADE, ForeignKey, Model, PositiveIntegerField, TextField, DateTimeField, CharField
from apps.authentication.models import User


class Post(Model):
    """User-created posts in the community."""
    
    author = ForeignKey(User, on_delete=CASCADE, related_name='posts')
    title = CharField(max_length=255)
    content = TextField()
    tags = CharField(max_length=255, blank=True)
    likes_count = PositiveIntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(Model):
    """Comments on posts."""
    
    post = ForeignKey(Post, on_delete=CASCADE, related_name='comments')
    author = ForeignKey(User, on_delete=CASCADE, related_name='comments')
    content = TextField()
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.email} on {self.post.title}"


class Like(Model):
    """User likes on posts."""
    
    post = ForeignKey(Post, on_delete=CASCADE, related_name='likes')
    user = ForeignKey(User, on_delete=CASCADE, related_name='likes')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} likes {self.post.title}"
