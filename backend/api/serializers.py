import base64

import webcolors
from django.core.files.base import ContentFile
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers


class Hex2NameColor(serializers.Field):
    '''Поле для перевода цвета из HEX в человекочитаемый язык'''

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для такого цвета имени нет!')
        return data


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор для тегов'''

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для ингридиентов'''

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class Base64ImageField(serializers.ImageField):
    '''Поле для загрузки картинки из Base64'''

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSlugField(serializers.SlugRelatedField):
    '''Кастомное слаг поле для тегов'''

    def to_representation(self, obj):
        serializers = TagSerializer(obj)
        return serializers.data


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для рецептов'''

    tags = TagSlugField(many=True, slug_field='id', queryset=Tag.objects.all())
    ingredients = IngredientSerializer(many=True, read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'image',
            'tags',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)
