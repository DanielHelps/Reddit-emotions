# Generated by Django 4.0.4 on 2022-06-24 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_sentence_sentence_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traindata',
            name='post_title',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]