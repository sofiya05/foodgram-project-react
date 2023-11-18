from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as UVS
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import SubscribeUserSerializer
from users.models import SubscribeUser

User = get_user_model()


class UserViewSet(UVS):
    @action(
        ["get", "put", "patch", "delete"],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        user = get_object_or_404(User, id=id)

        if request.user == user:
            return Response(
                {'errors': 'Вы не можете подписываться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if SubscribeUser.objects.filter(
            following=request.user, follower=user
        ).exists():
            return Response(
                {'errors': 'Вы уже подписаны на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        SubscribeUser.objects.create(following=request.user, follower=user)
        serializer = SubscribeUserSerializer(
            user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        user = get_object_or_404(User, id=id)
        if user == request.user:
            return Response(
                {'errors': 'Вы не можете отписываться от самого себя'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow = SubscribeUser.objects.filter(
            following=request.user, follower=user
        )
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'Вы уже отписались'}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get'],
        detail=False,
    )
    def subscriptions(self, request):
        lst = User.objects.filter(follower__following=request.user)

        queryset = self.filter_queryset(lst)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribeUserSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscribeUserSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)
