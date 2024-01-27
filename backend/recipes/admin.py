from django import forms
from django.contrib import admin

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class TagsForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )


class IngrediensInLine(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_favorites', 'list_ingredients')
    list_filter = ('author', 'name', 'tags')
    form = TagsForm
    model = Recipe
    inlines = (IngrediensInLine,)

    @admin.display(description='Кол-во добавлений в избранное')
    def count_favorites(self, obj):
        return obj.recipes_favoriterecipe_recipe.count()

    @admin.display(description='Список ингредиентов')
    def list_ingredients(self, obj):
        ingredients_list = [
            (
                f'{ingredient.ingredient} {ingredient.amount} '
                f'{ingredient.ingredient.measurement_unit}'
            )
            for ingredient in obj.recipes.all()
        ]
        return ', '.join(ingredients_list)


admin.site.register(ShoppingCart)
admin.site.register(FavoriteRecipe)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
