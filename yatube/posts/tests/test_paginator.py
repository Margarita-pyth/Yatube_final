
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Post, Group
from django.urls import reverse
from posts.views import POSTS_PER_PAGE

POSTS_ON_SECOND_PAGE = 3
User = get_user_model()


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Margo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.templates = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': cls.user})
        )

        number_of_posts = 13
        for post_num in range(number_of_posts):
            cls.post = Post.objects.create(author=cls.user, group=cls.group)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_index_profile_group_list_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        for reverse_name in PaginatorTests.templates:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
        self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)

    def test_second_index_profile_group_list_page_contains_three_records(self):
        """Проверка: количество постов на второй странице равно 3."""
        for reverse_name in PaginatorTests.templates:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get((reverse_name) + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         POSTS_ON_SECOND_PAGE)
