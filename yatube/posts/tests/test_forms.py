from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Post, Group, Comment
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import tempfile
from posts.models import User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Margo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.user,
            post=cls.post
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка создания нового поста с картитнкой в базе данных"""
        post_count = Post.objects.count()
        form_data = {
            'text': ['text'],
            'group': self.group.id,
            'image': self.post.image
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True,
        )
        # Проверяем, редирект после создания поста
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': self.user}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)

        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=self.post.text,
                group=self.group,
                image=self.post.image
            ).exists()
        )

    def test_post_edit(self):
        """Проверка редактирования поста в базе данных"""
        post_count = Post.objects.count()
        form_data = {
            'text': ['text'],
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.id}),
            data=form_data,
            follow=True,
        )
        # Проверяем, редирект после редактирования поста
        self.assertRedirects(response, reverse('posts:post_detail',
                                               args={self.post.id}
                                               ))
        # Проверяем, что число постов не увеличилось
        self.assertEqual(Post.objects.count(), post_count == 1)

        self.assertTrue(
            Post.objects.filter(
                author=self.user,
            ).exists()
        )

    def test_guest__cant_create_post(self):
        """Неавторизованный пользователь не может создать пост."""
        post_count = Post.objects.count()
        form_data = {
            'text': ['text'],
            'group': self.group.id,
            'image': self.post.image
        }
        response = self.guest_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, '/auth/login/?next=/create/')
        # Проверяем, что число постов не увеличилось
        self.assertEqual(Post.objects.count(), post_count == 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                image=self.post.image
            ).exists()
        )

    def test_guest_cant_edit_post(self):
        """Неавторизованный пользователь не может редактировать пост."""
        post_count = Post.objects.count()
        form_data = {
            'text': ['text'],
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', args={self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/edit/')
        # Проверяем, что число постов не увеличилось
        self.assertEqual(Post.objects.count(), post_count == 1)
        self.assertFalse(
            Post.objects.filter(
                text="Правим пост",
            ).exists()
        )

    def test_image_post_detail_(self):
        """Изображение передаётся в словаре context в post_detail."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={"post_id": self.post.id})
        )
        obj = response.context['post']
        self.assertEqual(obj.image, self.post.image)

    def test_image_index_profile_group_list_correct_context(self):
        """Изображение передаётся в словаре context."""
        templates_page_names = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': self.user}),
        )
        for reverse_name in templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post_object = response.context['page_obj'][0]
                post = post_object.image
                self.assertEqual(post, self.post.image)

    def test_authorized_client_add_comment(self):
        """Авторизованный пользователь может оставлять комментарии."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': ['text'],
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        # Проверяем, редирект после создания комментария
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': self.post.id}
                                               ))
        # Проверяем, увеличилось ли число комментариев
        self.assertEqual(Comment.objects.count(), comment_count + 1)

        self.assertTrue(
            Comment.objects.filter(
                text=self.comment.text,
                author=self.user,
                post=self.post.id
            ).exists()
        )

    def test_guest_client_cant_add_comment(self):
        """Неавторизованный пользователь не может оставить комментарии."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': ['text'],
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=False,
        )
        # Проверяем, редирект
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')
        # Проверяем, увеличилось ли число комментариев
        self.assertEqual(Comment.objects.count(), comment_count == 1)

        self.assertTrue(
            Comment.objects.filter(
                text=self.comment.text,
                author=self.user,
                post=self.post.id
            ).exists())
