from rest_framework import viewsets, filters

from api.serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
)
from recipes.models import Ingredient, Tag, Recipe

from django.contrib.auth import get_user_model

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-pub_date',)
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
