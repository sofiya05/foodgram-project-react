from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
    User,
)
from users.models import SubscribeUser


def check_have_obj(model):
    if not model:
        raise serializers.ValidationError(
            'Объект не найден!', code=status.HTTP_404_NOT_FOUND
        )


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
        return (
            self.context['request'].user.is_authenticated
            and obj.following.filter(
                user=self.context['request'].user
            ).exists()
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


class FavoriteRecipeSerializer(AbstractFavoriteShoppingCartSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')
        validators = (
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'recipe'),
            ),
        )


class ShoppingCartSerializer(AbstractFavoriteShoppingCartSerializer):
    """Сериализатор для списка покупок"""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = (
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'recipe'),
            ),
        )


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


class SubscribeUserSerializer(serializers.ModelSerializer):
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
        data = UserSerializer(instance.author, context=self.context).data
        limit = self.context.get('request').GET.get('recipes_limit')
        queryset = instance.author.recipes.all()
        if limit:
            try:
                queryset = queryset[: int(limit)]
            except ValueError as error:
                raise serializers.ValidationError(
                    {
                        'ValueError': (
                            'Ошибка преобразования'
                            f'limit в int. Error: {error}'
                        )
                    }
                )
        data['recipes'] = ShortRecipeSerializer(
            queryset, many=True, read_only=True, context=self.context
        ).data
        data['recipes_count'] = instance.author.recipes.count()
        return data


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
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Убедитесь, что это значение больше либо равно 1.'
            )
        return value


class PostRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = CreateIngredientRecipeSerializer(many=True)
    image = Base64ImageField()

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

    def check_unique_null_validate(self, list, field):
        if len(list) < 1:
            raise serializers.ValidationError(
                f'{field} не должны быть пустыми!'
            )
        if len(list) != len(set(list)):
            raise serializers.ValidationError(
                f'{field} должны быть уникальными!'
            )

    def validate_ingredients(self, value):
        id_ingredients_list = [
            ingredient['ingredient'] for ingredient in value
        ]
        self.check_unique_null_validate(id_ingredients_list, 'ingredinets')
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Поле image обязательное!')
        return value

    def validate_tags(self, value):
        self.check_unique_null_validate(value, 'tags')
        return value

    def to_representation(self, instance):
        return GetRecipeSerializer(
            instance, context={'request': self.context['request']}
        ).data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data, author=self.context['request'].user
        )
        recipe.tags.set(tags)
        recipe_ingredient_objects = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredient_objects)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        self.validate_ingredients(ingredients)
        self.validate_tags(validated_data.get('tags', []))
        super().update(instance, validated_data)
        instance.ingredients.clear()
        recipe_ingredient_objects = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredient_objects)
        return instance
