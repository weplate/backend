# Generated by Django 4.0.1 on 2022-05-03 19:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0017_alter_studentprofile_user_expopushtoken'),
    ]

    operations = [
        migrations.RenameField(
            model_name='expopushtoken',
            old_name='profile',
            new_name='user',
        ),
    ]
