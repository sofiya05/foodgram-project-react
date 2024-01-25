from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from foodgram_backend import constants


class User(AbstractUser):
    password = models.CharField(
        _('password'), max_length=constants.CHARACTERS_150
    )
    email = models.EmailField(
        _('email address'), max_length=constants.CHARACTERS_254, unique=True
    )
    first_name = models.CharField(
        _('first name'), max_length=constants.CHARACTERS_150
    )
    last_name = models.CharField(
        _('last name'), max_length=constants.CHARACTERS_150
    )
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class SubscribeUser(models.Model):
    user = models.ForeignKey(
        User, related_name='follower', on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE
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
