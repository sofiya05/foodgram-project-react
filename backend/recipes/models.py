from django.contrib.auth import get_user_model
from django.db import models
from recipes.validators import validate_time

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Имя ингредиента', max_length=100)
    measurement_unit = models.CharField('Единица измерения', max_length=20)

    class Meta:
        verbose_name = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=100)
    color = models.CharField('Цвет', max_length=16)
    slug = models.SlugField('Ссылка')

    class Meta:
        verbose_name = 'Теги'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='recipes', null=True
    )
    name = models.CharField('Название рецепта', max_length=200)
    image = models.ImageField('Изображение', upload_to='recipes/')
    text = models.TextField('Описание рецепта')
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    cooking_time = models.IntegerField(
        'Время на приготовление в минутах', validators=(validate_time,)
    )
    pub_date = models.DateTimeField(
        'Дата и время добавления', auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = 'Рецепты'

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
        verbose_name = 'Теги рецептов'

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
    amount = models.IntegerField('Количество')

    class Meta:
        verbose_name = 'Ингредиенты рецептов'

    def __str__(self) -> str:
        return f'Ингредиент: {self.ingredient}, Рецепт: {self.recipe}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe'
    )

    class Meta:
        verbose_name = 'Избранные рецепты'

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe',
            )
        ]

    def __str__(self) -> str:
        return f'Рецепт: {self.recipe}, id пользователя: {self.user}'


class ShopingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cart'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_shopping_cart',
            )
        ]
