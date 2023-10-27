from django.contrib import admin
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
