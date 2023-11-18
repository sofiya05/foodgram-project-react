from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    password = models.CharField(_('password'), max_length=150)
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    first_name = models.CharField(_('First_name'), max_length=150)
    last_name = models.CharField(_('Last_name'), max_length=150)
    REQUIRED_FIELDS = ('email', 'first_name', 'last_name')


class SubscribeUser(models.Model):
    following = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE
    )
    follower = models.ForeignKey(
        User, related_name='follower', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписки пользователя'
        constraints = [
            models.UniqueConstraint(
                fields=('following', 'follower'),
                name='unique_following_follower',
            )
        ]

    def __str__(self) -> str:
        return f'Пользователь {self.follower}, отслеживает {self.following}'
