from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Post, Comment, Like


class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'author_email', 'content', 'created_at')
        read_only_fields = ('id', 'author', 'author_email', 'created_at')


class PostSerializer(serializers.ModelSerializer):
    """Serializer for listing and retrieving posts with nested comments."""
    
    author_email = serializers.CharField(source='author.email', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'author', 'author_email', 'title', 'content', 'tags', 
                  'likes_count', 'is_liked', 'comments', 'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'author_email', 'likes_count', 'created_at', 'updated_at')

    @extend_schema_field(serializers.BooleanField())
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(post=obj, user=request.user).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating posts."""
    
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'tags', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
