# Generated by Django 2.1.7 on 2019-02-13 21:28

from django.db import migrations

from wells import data_migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wells', '0057_auto_20190211_2158'),
    ]

    operations = [
        migrations.RunPython(
            data_migrations.insert_unk_well_class_code, data_migrations.revert_unk_well_class_code),
    ]
