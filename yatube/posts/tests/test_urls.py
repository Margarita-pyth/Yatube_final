from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем общедоступные страницы
    def test_home_url_exists(self):
        """Страницы доступны любому пользователю."""
        templates_url_names = {
            '/',
            f'/group/{PostURLTests.group.slug}/',
            f'/profile/{PostURLTests.user.username}/',
            f'/posts/{PostURLTests.post.id}/'
        }
        for template in templates_url_names:
            with self.subTest(address=template):
                response = self.guest_client.get(template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """Страница 404 отдает кастомный шаблон."""
        response = self.guest_client.get('/posts/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_create_exists(self):
        """Страница /CREATE/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_exists(self):
        """Страница post_id_edit доступна автору."""
        self.user = User.objects.get(username=self.post.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_uses_correct_template(self):
        """Проверка шаблона для адреса /post_edit/."""
        self.user = User.objects.get(username=self.post.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
