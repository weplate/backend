# Generated by Django 4.0.1 on 2022-02-23 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_alter_mealitem_ingredients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mealitem',
            name='category',
            field=models.CharField(blank=True, choices=[('vegetable', 'Vegetable'), ('protein', 'Protein'), ('grain', 'Grains')], max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='activity_level',
            field=models.CharField(choices=[('sedentary', 'Sedentary'), ('mild', 'Mild Activity'), ('moderate', 'Moderate Activity'), ('heavy', 'Heavy or Labour Intensive Activity'), ('extreme', 'Extreme Activity')], max_length=64, verbose_name='Activity Level'),
        ),
    ]
