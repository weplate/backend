# Generated by Django 4.0.1 on 2022-02-23 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_mealitem_category_alter_mealitem_graphic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mealitem',
            name='ingredients',
            field=models.ManyToManyField(blank=True, to='backend.Ingredient'),
        ),
    ]
