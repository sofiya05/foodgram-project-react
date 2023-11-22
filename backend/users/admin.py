from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import SubscribeUser, User

admin.site.register(User, UserAdmin)
admin.site.register(SubscribeUser)
