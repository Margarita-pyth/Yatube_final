from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow
from posts.models import User


class PostFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Margo')
        cls.follower = User.objects.create(
            username='Stas'
        )

    def setUp(self):
        self.client_follower = Client()
        self.client_follower.force_login(PostFollowTests.follower)

    def test_follow(self):
        """Пользователь может подписаться."""
        self.assertEqual(Follow.objects.count(), 0)
        self.client_follower.get(reverse('posts:profile_follow', args=(
                                 PostFollowTests.author.username,)))
        self.assertEqual(Follow.objects.count(), 1)
        follow = Follow.objects.all()[0]
        self.assertEqual(follow.author, PostFollowTests.author)
        self.assertEqual(follow.user, PostFollowTests.follower)
        # Проверяет, что невозможна повторная подписка
        self.client_follower.get(reverse('posts:profile_follow', args=(
                                 PostFollowTests.author.username,)))
        self.assertEqual(Follow.objects.count(), 1)
        follows = Follow.objects.filter(author=PostFollowTests.author,
                                        user=PostFollowTests.follower)
        self.assertEqual(len(follows), 1)

    def test_unfollow(self):
        """Пользователь может отписаться."""
        self.assertEqual(Follow.objects.count(), 0)
        Follow.objects.create(author=PostFollowTests.author,
                              user=PostFollowTests.follower)
        self.assertEqual(Follow.objects.count(), 1)
        self.client_follower.get(reverse('posts:profile_unfollow', args=(
                                 PostFollowTests.author.username,)))
        self.assertEqual(Follow.objects.count(), 0)
        follows = Follow.objects.filter(author=PostFollowTests.author,
                                        user=PostFollowTests.follower)
        self.assertFalse(follows)
