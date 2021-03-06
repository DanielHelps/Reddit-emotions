# Generated by Django 4.0.4 on 2022-06-28 19:05

from django.db import migrations, models
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_classifiers'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classifier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classifier_obj', picklefield.fields.PickledObjectField(editable=False)),
                ('classifier_date', models.DateField()),
            ],
        ),
        migrations.DeleteModel(
            name='Classifiers',
        ),
    ]
