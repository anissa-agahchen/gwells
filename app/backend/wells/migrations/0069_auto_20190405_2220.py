# Generated by Django 2.1.8 on 2019-04-05 22:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wells', '0068_merge_20190328_2059'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activitysubmission',
            old_name='ems_id',
            new_name='ems',
        ),
    ]
