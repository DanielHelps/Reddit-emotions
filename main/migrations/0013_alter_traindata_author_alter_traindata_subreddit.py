# Generated by Django 4.0.4 on 2022-06-08 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_traindata_author_traindata_subreddit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traindata',
            name='author',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='traindata',
            name='subreddit',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
