# Generated by Django 4.0.1 on 2022-02-23 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_alter_mealitem_name_alter_mealselection_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealitem',
            name='category',
            field=models.CharField(blank=True, choices=[('vegetable', 'Vegetable'), ('protein', 'Protein'), ('carbohydrate', 'Carbohydrate')], max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='mealitem',
            name='graphic',
            field=models.FileField(blank=True, null=True, upload_to='assets/meal_items/'),
        ),
    ]
