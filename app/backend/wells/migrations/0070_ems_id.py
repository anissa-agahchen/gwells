# Generated by Django 2.1.8 on 2019-04-08 15:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wells', '0069_auto_20190405_2220'),
    ]

    operations = [
        migrations.RunSQL("""
        UPDATE well
        SET ems = ems_id
        WHERE ems IS NULL AND ems_id IS NOT NULL;
        """)
    ]
