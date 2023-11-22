from api.views import (IngredientViewSet, RecipeViewSet, ShopingCartAPIView,
                       TagViewSet)
from django.urls import include, path
from rest_framework import routers

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'recipes/<int:id>/shopping_cart/',
        ShopingCartAPIView.as_view(),
        name='shopping_cart',
    ),
]
