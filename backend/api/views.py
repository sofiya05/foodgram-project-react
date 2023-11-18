from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    TagSerializer,
)
from foodgram_backend.filters import AuthorAndTagFilter
from foodgram_backend.permissions import IsAuthorizedOwnerOrReadOnly
from recipes.models import FavoriteRecipe, Ingredient, Recipe, ShopingCart, Tag

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = ('name',)
    pagination_class = None
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'errors': 'Такого рецепта не существует!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
                return Response(
                    ShortRecipeSerializer(recipe).data,
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError:
                return Response(
                    {'errors': 'Этот рецепт уже добавлен в избранное!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            try:
                self.perform_destroy(
                    FavoriteRecipe.objects.get(
                        user=request.user,
                        recipe=get_object_or_404(Recipe, pk=pk),
                    )
                )
            except FavoriteRecipe.DoesNotExist:
                return Response(
                    {'errors': 'Этот не добавлен в избранное!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        cart_dict = {}
        user = request.user
        for cart in user.cart.all():
            for ingredient in cart.recipe.recipes.all():
                if ingredient.ingredient.name not in cart_dict.keys():
                    cart_dict[ingredient.ingredient.name] = ingredient.amount
                else:
                    cart_dict[ingredient.ingredient.name] += ingredient.amount

        file = open(
            user.username + '_shopping_cart.txt', 'w', encoding='UTF-8'
        )
        file.write('Список покупок пользователя: ' + user.username + '\n')
        for key, value in cart_dict.items():
            file.write(key + ': ' + str(value) + '\n')
        file.close()
        file = open(
            user.username + '_shopping_cart.txt', 'r', encoding='UTF-8'
        )
        response = HttpResponse(file, content_type='whatever')
        response['Content-Disposition'] = (
            'attachment; filename="%s"' % file.name
        )
        return response


# пыталась делать этот класс на viewsets
# и миксинах но роутер по непонятным причинам
# ограничивал метод delete и ему было все равно
# явно указаны доступные методы или нет
class ShopingCartAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            recipe = Recipe.objects.get(pk=kwargs.get('id'))
            ShopingCart.objects.create(recipe=recipe, user=request.user)
            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            return Response(
                {'errors': 'Этот рецепт уже добавлен в список покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Recipe.DoesNotExist:
            return Response(
                {'errors': 'Такого рецепта не сущестует!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        try:
            ShopingCart.objects.get(
                recipe=get_object_or_404(Recipe, pk=kwargs.get('id')),
                user=request.user,
            ).delete()
        except ShopingCart.DoesNotExist:
            return Response(
                {'errors': 'Этот рецепт не добавлен в ваш список покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
