# Generated by Django 4.0.4 on 2022-05-07 12:07

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0002_alter_emot_search_db_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='emot_search_db',
            new_name='SearchQ',
        ),
    ]
