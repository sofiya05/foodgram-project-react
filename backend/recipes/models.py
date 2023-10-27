from django.contrib.auth import get_user_model
from django.db import models

from recipes.validators import validate_time

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Имя ингридиента', max_length=100)
    measurement_unit = models.CharField('Единица измерения', max_length=5)

    class Meta:
        verbose_name = 'Ингридиенты'

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
        User, on_delete=models.CASCADE, related_name='recipes'
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
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.IntegerField('Количество')

    def __str__(self) -> str:
        return f'{self.ingredient} {self.recipe}'
