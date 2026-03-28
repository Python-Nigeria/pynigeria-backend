from rest_framework.test import APITransactionTestCase
from rest_framework import status
from django.urls import reverse
from apps.authentication.models import User
from apps.community.models import Post, Comment, Like


class PostListCreateViewTestCase(APITransactionTestCase):
    """Tests for PostListCreateView."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='otheruser@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test content'
        )
        self.url = reverse('post-list')
    
    def test_list_posts_unauthenticated(self):
        """Test that unauthenticated users can list posts."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_post_authenticated(self):
        """Test that authenticated users can create posts."""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Post',
            'content': 'New content',
            'tags': 'test'
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Post')
    
    def test_create_post_unauthenticated(self):
        """Test that unauthenticated users cannot create posts."""
        data = {
            'title': 'New Post',
            'content': 'New content'
        }
        response = self.client.post(self.url, data=data)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class PostRetrieveUpdateDeleteViewTestCase(APITransactionTestCase):
    """Tests for PostRetrieveUpdateDeleteView."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='otheruser@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test content'
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.other_user,
            content='Test comment'
        )
        self.url = reverse('post-detail', kwargs={'pk': self.post.id})
    
    def test_retrieve_post_with_comments(self):
        """Test that post detail includes comments."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')
        self.assertEqual(len(response.data['comments']), 1)
        self.assertEqual(response.data['comments'][0]['content'], 'Test comment')
    
    def test_update_post_owner(self):
        """Test that owner can update post."""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Title', 'content': 'Updated content'}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
    
    def test_update_post_non_owner(self):
        """Test that non-owner cannot update post."""
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'Updated Title', 'content': 'Updated content'}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_post_owner(self):
        """Test that owner can delete post."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())
    
    def test_delete_post_non_owner(self):
        """Test that non-owner cannot delete post."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentCreateViewTestCase(APITransactionTestCase):
    """Tests for CommentCreateView."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test content'
        )
        self.url = reverse('comment-create', kwargs={'pk': self.post.id})
    
    def test_create_comment_authenticated(self):
        """Test that authenticated users can comment."""
        self.client.force_authenticate(user=self.user)
        data = {'content': 'Test comment'}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.data['content'], 'Test comment')
    
    def test_create_comment_unauthenticated(self):
        """Test that unauthenticated users cannot comment."""
        data = {'content': 'Test comment'}
        response = self.client.post(self.url, data=data)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_create_comment_on_nonexistent_post(self):
        """Test creating comment on non-existent post."""
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-create', kwargs={'pk': 9999})
        data = {'content': 'Test comment'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentDeleteViewTestCase(APITransactionTestCase):
    """Tests for CommentDeleteView."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='otheruser@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test content'
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        self.url = reverse('comment-delete', 
                          kwargs={'pk': self.post.id, 'comment_id': self.comment.id})
    
    def test_delete_comment_author(self):
        """Test that comment author can delete comment."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())
    
    def test_delete_comment_non_author(self):
        """Test that non-author cannot delete comment."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_comment_unauthenticated(self):
        """Test that unauthenticated users cannot delete comments."""
        response = self.client.delete(self.url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_delete_nonexistent_comment(self):
        """Test deleting non-existent comment."""
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-delete', 
                     kwargs={'pk': self.post.id, 'comment_id': 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikeToggleViewTestCase(APITransactionTestCase):
    """Tests for LikeToggleView."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test content'
        )
        self.url = reverse('post-like', kwargs={'pk': self.post.id})
    
    def test_like_post_authenticated(self):
        """Test that authenticated users can like a post."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'liked')
        self.assertEqual(response.data['likes_count'], 1)
        self.assertTrue(Like.objects.filter(post=self.post, user=self.user).exists())
    
    def test_unlike_post(self):
        """Test that liking again unlikes the post (toggle)."""
        self.client.force_authenticate(user=self.user)
        # Like
        self.client.post(self.url)
        # Unlike
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'unliked')
        self.assertEqual(response.data['likes_count'], 0)
        self.assertFalse(Like.objects.filter(post=self.post, user=self.user).exists())
    
    def test_like_toggle_multiple_times(self):
        """Test toggling like multiple times."""
        self.client.force_authenticate(user=self.user)
        # Like
        response1 = self.client.post(self.url)
        self.assertEqual(response1.data['likes_count'], 1)
        # Unlike
        response2 = self.client.post(self.url)
        self.assertEqual(response2.data['likes_count'], 0)
        # Like again
        response3 = self.client.post(self.url)
        self.assertEqual(response3.data['likes_count'], 1)
    
    def test_like_post_unauthenticated(self):
        """Test that unauthenticated users cannot like posts."""
        response = self.client.post(self.url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_like_nonexistent_post(self):
        """Test liking non-existent post."""
        self.client.force_authenticate(user=self.user)
        url = reverse('post-like', kwargs={'pk': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_multiple_users_like_post(self):
        """Test that multiple users can like the same post."""
        user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        # User 1 likes
        self.client.force_authenticate(user=self.user)
        response1 = self.client.post(self.url)
        self.assertEqual(response1.data['likes_count'], 1)
        
        # User 2 likes
        self.client.force_authenticate(user=user2)
        response2 = self.client.post(self.url)
        self.assertEqual(response2.data['likes_count'], 2)


class PostListViewWithLikeStatusTestCase(APITransactionTestCase):
    """Tests for is_liked field in post serializer."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test content'
        )
        self.url = reverse('post-list')
    
    def test_is_liked_false_when_not_liked(self):
        """Test is_liked is false when user hasn't liked post."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data[0]['is_liked'])
    
    def test_is_liked_true_when_liked(self):
        """Test is_liked is true when user has liked post."""
        Like.objects.create(post=self.post, user=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data[0]['is_liked'])
    
    def test_is_liked_false_for_unauthenticated(self):
        """Test is_liked is false for unauthenticated users."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data[0]['is_liked'])
