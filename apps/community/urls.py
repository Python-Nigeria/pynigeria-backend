from django.urls import path
from .views import (
    PostListCreateView,
    PostRetrieveUpdateDeleteView,
    CommentCreateView,
    CommentDeleteView,
    LikeToggleView,
)

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list'),
    path('<int:pk>/', PostRetrieveUpdateDeleteView.as_view(), name='post-detail'),
    path('<int:pk>/comment/', CommentCreateView.as_view(), name='comment-create'),
    path('<int:pk>/comment/<int:comment_id>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('<int:pk>/like/', LikeToggleView.as_view(), name='post-like'),
]
