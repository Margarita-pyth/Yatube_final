from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel
from django.db.models import UniqueConstraint

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Название группы", max_length=200,
                             help_text='Добавьте название')
    slug = models.SlugField("Идентификатор группы", unique=True,
                            help_text='Добавьте идентификатор')
    description = models.TextField("Описание",
                                   help_text='Добавьте описание')

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField("Текст поста",
                            help_text='Добавьте содержимое поста')
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор",
        help_text='Выберите автора'
    )
    group = models.ForeignKey(
        Group(),
        models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name="Группа",
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date', ]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField()

    def __str__(self) -> str:
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )
    UniqueConstraint(fields=['user', 'author'],
                     name='unique_follow')
