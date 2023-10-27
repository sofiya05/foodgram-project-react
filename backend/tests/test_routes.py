from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

from recipes.models import Tag, Ingredient, Recipe


class TestRouters(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(username='Test User')
        cls.tag = Tag.objects.create(
            name='Тестовый тег', color='#E26C2D', slug='test_tag'
        )
        cls.ingredient = Ingredient.objects.create(
            name='Тестовый ингридиент', measurement_unit='кг'
        )
        cls.recipe = Recipe.objects.create(
            author=cls.user,
            name='Тестовый рецепт',
        )

    def test_endpoints(self):
        '''Тест доступности эндпоинтов анонимным пользователем'''
        urls = (
            ('api:tags-list', None),
            ('api:tags-detail', (self.tag.id,)),
            ('api:ingredients-list', None),
            ('api:ingredients-detail', (self.ingredient.id)),
            ('api:recipes-list', None),
            ('api:recipes-detail', self.recipe.id),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
