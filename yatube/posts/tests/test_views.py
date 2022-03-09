
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group
from django import forms

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Margo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.another_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:create_post'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html'
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем, что словарь context страниц index, group_list, profile
    #  содержaт ожидаемые значения
    def test_index_profile_group_pages_show_correct_context(self):
        """Шаблон index/group_list/profile сформирован с верным контекстом."""
        templates_page_names = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': self.user})
        )
        for reverse_name in templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post_object = response.context['page_obj'][0]
                post_text = post_object.text
                self.assertEqual(post_text, 'Тестовый пост')
                post_author = post_object.author
                self.assertEqual(post_author, self.post.author)
                post_group = post_object.group
                self.assertEqual(post_group, self.post.group)
                self.assertNotIn(reverse('posts:group_posts',
                                         kwargs={'slug': 'test-slug-2'}),
                                 'Тестовый пост')

    # Проверяем, что словарь context страницы post_detail
    #  содержат ожидаемые значения
    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с верным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_create_edit_post_form__show_correct_context(self):
        """Шаблон создания/редакции поста сформирован с верным контекстом."""
        templates_page_names = {
            reverse('posts:create_post'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        }
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for reverse_name in templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_index_cached(self):
        """Проверка кеширования главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        cache = response.content
        post_delete = Post.objects.get(id=1)
        post_delete.delete()
        cache_after_delete = self.authorized_client.get(reverse('posts:index'))
        cache_after = cache_after_delete.content
        self.assertTrue(cache == cache_after)
