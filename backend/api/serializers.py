import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShopingCart,
    Tag,
)
from users.serializers import UserSerializer

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Поле для загрузки картинки из Base64"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')

    def create(self, validated_data):
        recipe = Recipe.objects.get(pk=validated_data.get('recipe'))
        FavoriteRecipe.objects.create(
            user=validated_data.get('user'),
            recipe=recipe,
        )

        serializer = ShortRecipeSerializer(recipe)

        return serializer.data()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов"""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок"""

    class Meta:
        model = ShopingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Ингредиенты для рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSlugField(serializers.SlugRelatedField):
    """Кастомное слаг поле для тегов"""

    def to_representation(self, obj):
        serializer = TagSerializer(obj)
        return serializer.data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""

    tags = TagSlugField(many=True, slug_field='id', queryset=Tag.objects.all())
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        if not ingredients or not tags:
            raise serializers.ValidationError(
                {'errors': 'Поле ингредиентов и тегов не должно быть пустым!'}
            )
        list_ingredients = []
        list_tags = []
        for i in ingredients:
            if not Ingredient.objects.filter(pk=i['id']).exists():
                raise serializers.ValidationError(
                    {'errors': 'Такого ингредиента не существует!'}
                )
            amount = i['amount']
            if int(amount) < 1:
                raise serializers.ValidationError(
                    {'amount': 'Количество ингредиента должно быть больше 0!'}
                )
            if i['id'] in list_ingredients:
                raise serializers.ValidationError(
                    {'errors': 'Ингредиенты должны быть уникальными!'}
                )
            list_ingredients.append(i['id'])
        for t in tags:
            if not Tag.objects.filter(pk=t).exists():
                raise serializers.ValidationError(
                    {'errors': 'Такого тега не существует!'}
                )
            if t in list_tags:
                raise serializers.ValidationError(
                    {'errors': 'Теги должны быть уникальными'}
                )
            list_tags.append(t)
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

        for value in self.initial_data['ingredients']:
            ingredient = Ingredient.objects.get(id=value['id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=value['amount'],
            )
        return recipe

    def check_user_exists(self, user, exists):
        if user.is_authenticated:
            exists
        else:
            return False

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.user.filter(recipe=obj).exists()
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.cart.filter(recipe=obj).exists()
        else:
            return False

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=obj), many=True
        ).data


# при импорте ShortRecipeSerializer в users.serializers
# возникала ошибка рекурсии, перенесла сюда
class SubscribeUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        limit = self.context.get('request').GET.get('recipes_limit')
        user = User.objects.get(pk=obj.pk)
        queryset = user.recipes.all()
        if limit:
            queryset = queryset[: int(limit)]
        return ShortRecipeSerializer(queryset, many=True, read_only=True).data
