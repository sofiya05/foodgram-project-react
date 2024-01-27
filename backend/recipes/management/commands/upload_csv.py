import csv
import os
from typing import Any

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    def upload(self, data, model):
        models = []
        for row in data:
            models.append(model(**row))
        return model.objects.bulk_create(models)

    def handle(self, *args: Any, **options: Any):
        path = os.getcwd() + '/data'
        if 'ingredients.csv' and 'tags.csv' not in os.listdir(path):
            raise FileNotFoundError(
                'Файл ingredients.csv или tags.csv не найден!'
            )
        Ingredient.objects.all().delete()
        Tag.objects.all().delete()
        try:
            for filename in os.listdir(path):
                with open(
                    os.path.join(path, filename), 'r', encoding='UTF-8'
                ) as file:
                    file_reader = csv.DictReader(file)
                    if filename == 'ingredients.csv':
                        self.upload(file_reader, Ingredient)
                        self.stdout.write(
                            'Upload Ingredients\t\t'
                            + '\033[32m{}'.format('OK')
                            + '\033[0m'
                        )
                    elif filename == 'tags.csv':
                        self.upload(file_reader, Tag)
                        self.stdout.write(
                            'upload tags\t\t'
                            + '\033[32m{}'.format('OK')
                            + '\033[0m'
                        )
        except IOError as error:
            raise IOError(f'Ошибка открытия файла: {error}')
