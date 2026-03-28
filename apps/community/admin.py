from django.contrib import admin
from .models import Post, Comment, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'likes_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content', 'author__email')
    readonly_fields = ('created_at', 'updated_at', 'likes_count')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__email', 'post__title')
    readonly_fields = ('created_at',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'post__title')
    readonly_fields = ('created_at',)
