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
        model.objects.bulk_create(models)

    def handle(self, *args: Any, **options: Any):
        path = '../data/'
        for filename in os.listdir(path):
            with open(
                os.path.join(path, filename), 'r', encoding='UTF-8'
            ) as file:
                file_reader = csv.DictReader(file)
                if filename == 'ingredients.csv':
                    self.upload(file_reader, Ingredient)
                elif filename == 'tags.csv':
                    self.upload(file_reader, Tag)
        print('done!')
