# Generated by Django 4.0.1 on 2022-03-07 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_studentprofile_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealitem',
            name='cafeteria_id',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]