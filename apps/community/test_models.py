from django.test import TestCase
from django.db import IntegrityError
from apps.authentication.models import User
from apps.community.models import Post, Comment, Like


class PostModelTestCase(TestCase):
    """Tests for Post model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
    
    def test_create_post(self):
        """Test creating a post."""
        post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test content',
            tags='python,django'
        )
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.likes_count, 0)
    
    def test_post_str_representation(self):
        """Test post string representation."""
        post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test content'
        )
        self.assertEqual(str(post), 'Test Post')
    
    def test_post_ordering(self):
        """Test posts are ordered by created_at descending."""
        post1 = Post.objects.create(author=self.user, title='Post 1', content='Content 1')
        post2 = Post.objects.create(author=self.user, title='Post 2', content='Content 2')
        
        posts = list(Post.objects.all())
        self.assertEqual(posts[0].id, post2.id)
        self.assertEqual(posts[1].id, post1.id)


class CommentModelTestCase(TestCase):
    """Tests for Comment model."""
    
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
    
    def test_create_comment(self):
        """Test creating a comment."""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        self.assertEqual(comment.content, 'Test comment')
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)
    
    def test_comment_str_representation(self):
        """Test comment string representation."""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        expected_str = f"Comment by {self.user.email} on {self.post.title}"
        self.assertEqual(str(comment), expected_str)
    
    def test_comment_on_deleted_post(self):
        """Test that comments are deleted when post is deleted."""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        self.post.delete()
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())


class LikeModelTestCase(TestCase):
    """Tests for Like model."""
    
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
    
    def test_create_like(self):
        """Test creating a like."""
        like = Like.objects.create(post=self.post, user=self.user)
        self.assertEqual(like.post, self.post)
        self.assertEqual(like.user, self.user)
    
    def test_like_str_representation(self):
        """Test like string representation."""
        like = Like.objects.create(post=self.post, user=self.user)
        expected_str = f"{self.user.email} likes {self.post.title}"
        self.assertEqual(str(like), expected_str)
    
    def test_unique_together_constraint(self):
        """Test that a user cannot like the same post twice."""
        Like.objects.create(post=self.post, user=self.user)
        
        with self.assertRaises(IntegrityError):
            Like.objects.create(post=self.post, user=self.user)
    
    def test_like_on_deleted_post(self):
        """Test that likes are deleted when post is deleted."""
        like = Like.objects.create(post=self.post, user=self.user)
        self.post.delete()
        self.assertFalse(Like.objects.filter(id=like.id).exists())
