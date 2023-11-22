# Generated by Django 3.2.16 on 2023-11-22 18:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0003_alter_ingredient_measurement_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipetag',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipesTag',
                to='recipes.recipe',
            ),
        ),
        migrations.AlterField(
            model_name='recipetag',
            name='tag',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='tagsRecipes',
                to='recipes.tag',
            ),
        ),
    ]
