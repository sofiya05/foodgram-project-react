from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from foodgram_backend import constants


class User(AbstractUser):
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
    USERNAME_FIELD = 'email'
    email = models.EmailField(
        _('email address'),
        max_length=constants.LIMITATION_CHARACTERS_EMAIL,
        unique=True,
    )
    first_name = models.CharField(
        _('first name'),
        max_length=constants.LIMITATION_CHARACTERS_STANDART_USER_FIELDS,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=constants.LIMITATION_CHARACTERS_STANDART_USER_FIELDS,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class SubscribeUser(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписки пользователя'
        verbose_name_plural = 'Подписки пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following_follower',
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        ]

    def __str__(self) -> str:
        return f'Пользователь {self.user}, отслеживает {self.author}'
