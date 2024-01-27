from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as UVS
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action

from api.filters import AuthorAndTagFilter, IngredientFilter
from api.permissions import IsAuthorizedOwnerOrReadOnly
from api.serializers import (
    CreateSubscribeUserSerializer,
    FavoriteRecipeSerializer,
    GetRecipeSerializer,
    IngredientSerializer,
    PostRecipeSerializer,
    ShoppingCartSerializer,
    SubscribeUserSerializer,
    TagSerializer,
)
from api.view_methods import create_file, create_obj, mapping_delete
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import SubscribeUser, User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects.all()
        .select_related('author')
        .prefetch_related('tags', 'ingredients')
    )
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = AuthorAndTagFilter
    permission_classes = (IsAuthorizedOwnerOrReadOnly,)
    ordering = ('-pub_date',)
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return PostRecipeSerializer

    @action(methods=['POST'], detail=True)
    def favorite(self, request, pk=None):
        return create_obj(
            FavoriteRecipeSerializer, {'user': request.user.pk, 'recipe': pk}
        )

    @favorite.mapping.delete
    def del_favorite(self, request, pk=None):
        get_object_or_404(Recipe, pk=pk)
        return mapping_delete(
            FavoriteRecipe.objects.filter(user=request.user, recipe_id=pk),
            'Этот рецепт не добавлен в избранное!',
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticatedOrReadOnly,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__recipes_shoppingcart_recipe__user=request.user
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
        )
        return create_file(request, ingredients)

    @action(methods=['POST'], detail=True)
    def shopping_cart(self, request, pk=None):
        return create_obj(
            ShoppingCartSerializer, {'user': request.user.pk, 'recipe': pk}
        )

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, pk=None):
        get_object_or_404(Recipe, pk=pk)
        return mapping_delete(
            ShoppingCart.objects.filter(user=request.user, recipe_id=pk),
            'Этот рецепт не добавлен в ваш список покупок!',
        )


class UserViewSet(UVS):
    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        get_object_or_404(User, pk=id)
        return create_obj(
            CreateSubscribeUserSerializer,
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
        data = User.objects.filter(following__user=request.user)
        print(data)
        page = self.paginate_queryset(data)
        serializer = SubscribeUserSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
