from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from .models import Post, Comment, Like
from .serializers import PostSerializer, PostCreateSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly


class PostListCreateView(generics.ListCreateAPIView):
    """
    List all posts (public) or create a new post (authenticated only).
    """
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @extend_schema(
        tags=['Community'],
        operation_id='list_posts',
        description='List all community posts. Public endpoint.'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['Community'],
        operation_id='create_post',
        description='Create a new community post. Authenticated users only.'
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class PostRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve a post with its comments (public).
    Update or delete a post (owner only).
    """
    queryset = Post.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return PostCreateSerializer
        return PostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @extend_schema(
        tags=['Community'],
        operation_id='retrieve_post',
        description='Retrieve a single post with its comments. Public endpoint.'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=['Community'],
        operation_id='update_post',
        description='Update a post. Post owner only.'
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=['Community'],
        operation_id='destroy_post',
        description='Delete a post. Post owner or admin only.'
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CommentCreateView(generics.CreateAPIView):
    """
    Add a comment to a post (authenticated only).
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs.get('pk'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Community'],
        operation_id='create_comment',
        description='Add a comment to a post. Authenticated users only.'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CommentDeleteView(generics.DestroyAPIView):
    """
    Delete a comment (comment author or admin only).
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        comment = get_object_or_404(Comment, pk=self.kwargs.get('comment_id'), post__pk=self.kwargs.get('pk'))
        
        # Check if user is the author or admin
        if comment.author != self.request.user and not self.request.user.is_staff:
            self.permission_denied(self.request)
        
        return comment

    @extend_schema(
        tags=['Community'],
        operation_id='delete_comment',
        description='Delete a comment. Comment author or admin only.'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class LikeToggleView(APIView):
    """
    Toggle like/unlike on a post (authenticated only).
    If user already liked, unlike it. If not, like it.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Community'],
        operation_id='toggle_post_like',
        description='Toggle like/unlike on a post. If already liked, unlikes it; otherwise likes it. Authenticated users only.'
    )
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like = Like.objects.filter(post=post, user=request.user).first()

        if like:
            # Unlike
            like.delete()
            post.likes_count -= 1
            post.save()
            return Response(
                {'status': 'unliked', 'likes_count': post.likes_count},
                status=status.HTTP_200_OK
            )
        else:
            # Like
            Like.objects.create(post=post, user=request.user)
            post.likes_count += 1
            post.save()
            return Response(
                {'status': 'liked', 'likes_count': post.likes_count},
                status=status.HTTP_201_CREATED
            )
