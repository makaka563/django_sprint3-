from django.db import models
from django.contrib.auth import get_user_model


class AbstracModel(models.Model):
    is_published = models.BooleanField(
        blank=False,
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        blank=False,
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


User = get_user_model()


class Category(AbstracModel):
    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        blank=False,
        verbose_name='Описание'
    )
    slug = models.SlugField(
        blank=False,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.',
        unique=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(AbstracModel):
    name = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(AbstracModel):
    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='title'
    )
    text = models.TextField(
        blank=False,
        verbose_name='Текст'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='image'
    )
    pub_date = models.DateTimeField(
        blank=False,
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в '
                  'будущем — можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        null=False,
        related_name='authors',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        related_name='locations',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        blank=False,
        on_delete=models.SET_NULL,
        null=True,
        related_name='categoties',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='post'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='author'
    )
    text = models.TextField(
        verbose_name='text'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='created_at'
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'comment'
        verbose_name_plural = 'comments'

    def __str__(self):
        return self.text[:50]
