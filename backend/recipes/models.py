from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram_backend import constants

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Имя ингредиента', max_length=constants.CHARACTERS_100
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=constants.CHARACTERS_20
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit',
            ),
        )

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Название тега', max_length=constants.CHARACTERS_100
    )
    color = ColorField('Цвет')
    slug = models.SlugField('Ссылка')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='recipes', null=True
    )
    name = models.CharField(
        'Название рецепта', max_length=constants.CHARACTERS_200
    )
    image = models.ImageField('Изображение', upload_to='recipes/')
    text = models.TextField('Описание рецепта')
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время на приготовление в минутах',
        validators=(MinValueValidator(1), MaxValueValidator(10000)),
    )
    pub_date = models.DateTimeField(
        'Дата и время добавления', auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipesTag'
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name='tagsRecipes'
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self) -> str:
        return f'Рецепт: {self.recipe}, Тег: {self.tag}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredients',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(MinValueValidator(1), MaxValueValidator(10000)),
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self) -> str:
        return f'''Ингредиент: {self.ingredient},
        Рецепт: {self.recipe}, Количество: {self.amount}'''


class AbstractFavoriteShoppingModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_user',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_recipe',
    )

    class Meta:
        abstract = True


class FavoriteRecipe(AbstractFavoriteShoppingModel):
    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_user_recipe'
            ),
        )

    def __str__(self) -> str:
        return f'Рецепт: {self.recipe}, id пользователя: {self.user}'


class ShoppingCart(AbstractFavoriteShoppingModel):
    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_shopping_cart',
            )
        ]

    def __str__(self) -> str:
        return f'Список покупок пользователя {self.user}'
