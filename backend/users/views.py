from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as UVS
from rest_framework import permissions
from rest_framework.decorators import action

from api.serializers import SubscribeUserSerializer
from foodgram_backend.methods import create_obj, mapping_delete
from recipes.models import User
from users.models import SubscribeUser


class UserViewSet(UVS):
    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        get_object_or_404(User, pk=id)
        return create_obj(
            SubscribeUserSerializer,
            {'user': request.user.pk, 'author': id},
            {'request': request},
        )

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        get_object_or_404(User, pk=id)
        return mapping_delete(
            SubscribeUser.objects.filter(user=request.user, author__id=id),
            'Вы не подписаны на этого пользователя!',
        )

    @action(
        methods=['get'],
        detail=False,
    )
    def subscriptions(self, request):
        data = request.user.follower.all()
        page = self.paginate_queryset(data)
        serializer = SubscribeUserSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
