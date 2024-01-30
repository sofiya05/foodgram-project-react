from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from foodgram_backend.constants import MAX_VALUE, MIN_VALUE
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import SubscribeUser, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated and obj.following.filter(user=user).exists()
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


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


class AbstractFavoriteShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe, read_only=True).data

    def validate(self, attrs):
        if self.Meta.model.objects.filter(
            user=attrs['user'], recipe=attrs['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Пара user, recipe должны быть уникальными!'
            )
        return attrs


class FavoriteRecipeSerializer(AbstractFavoriteShoppingCartSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')


class ShoppingCartSerializer(AbstractFavoriteShoppingCartSerializer):
    """Сериализатор для списка покупок"""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Ингредиенты для рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


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
        limit = self.context.get('request').GET.get('recipes_limit', None)
        queryset = obj.recipes.all()
        if limit:
            try:
                queryset = queryset[: int(limit)]
            except ValueError:
                pass
        return ShortRecipeSerializer(
            queryset, many=True, read_only=True, context=self.context
        ).data


class CreateSubscribeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribeUser
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=SubscribeUser.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя!',
            ),
        ]

    def validate(self, attrs):
        if attrs['user'] == attrs['author']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя!'
            )
        return attrs

    def to_representation(self, instance):
        return SubscribeUserSerializer(
            instance.author, context=self.context
        ).data


class GetRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True, many=True, source='recipes'
    )
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
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.recipes_favoriterecipe_user.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.recipes_shoppingcart_user.filter(recipe=obj).exists()
        )


class CreateIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_VALUE, max_value=MAX_VALUE)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class PostRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = CreateIngredientRecipeSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE, max_value=MAX_VALUE
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def check_unique_null_validate(self, list_obj, field):
        if not list_obj:
            raise serializers.ValidationError(
                f'{field} не должны быть пустыми!'
            )
        if len(list_obj) != len(set(list_obj)):
            raise serializers.ValidationError(
                f'{field} должны быть уникальными!'
            )

    def validate(self, attrs):
        id_ingredients_list = [
            ingredient['id'] for ingredient in attrs.get('ingredients', [])
        ]
        self.check_unique_null_validate(id_ingredients_list, 'ingredinets')

        return attrs

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Поле image обязательное!')
        return value

    def validate_tags(self, value):
        self.check_unique_null_validate(value, 'tags')
        return value

    def to_representation(self, instance):
        return GetRecipeSerializer(instance, context=self.context).data

    @staticmethod
    def create_obj(recipe, ingredients):
        recipe_ingredient_objects = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredient_objects)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data, author=self.context['request'].user
        )
        recipe.tags.set(tags)
        self.create_obj(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        self.validate_tags(validated_data.get('tags', []))
        super().update(instance, validated_data)
        instance.ingredients.clear()
        self.create_obj(instance, ingredients)
        return instance
