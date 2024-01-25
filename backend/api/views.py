from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action

from api.filters import AuthorAndTagFilter, IngredientFilter
from api.permissions import IsAuthorizedOwnerOrReadOnly
from api.serializers import (
    FavoriteRecipeSerializer,
    GetRecipeSerializer,
    IngredientSerializer,
    PostRecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from foodgram_backend.methods import create_file, create_obj, mapping_delete
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)

User = get_user_model()


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
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            (
                ShoppingCart.objects.filter(
                    recipe__recipes_shoppingcart_recipe__user=request.user
                )
            )
            .values(
                'recipe__recipes__ingredient__name',
                'recipe__recipes__ingredient__measurement_unit',
            )
            .annotate(amount=Sum('recipe__recipes__amount'))
        )
        file = create_file(request, ingredients)
        return FileResponse(open(file.name, 'rb'))

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
