# Generated by Django 4.0.4 on 2022-06-28 19:23

from django.db import migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_classifier_delete_classifiers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classifier',
            name='classifier_obj',
            field=picklefield.fields.PickledObjectField(editable=False, null=True),
        ),
    ]
