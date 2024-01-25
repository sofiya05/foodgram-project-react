from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import SubscribeUser, User


@admin.register(User)
class UserAdm(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'recipes_count',
        'followers_count',
    )

    def recipes_count(self, obj):
        return obj.recipes.count()

    def followers_count(self, obj):
        return obj.follower.count()


admin.site.register(SubscribeUser)
