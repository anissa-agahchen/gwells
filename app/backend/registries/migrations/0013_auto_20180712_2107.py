# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-12 21:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registries', '0001_squashed_0012_auto_20180704_2105'),
        ('gwells', '0001_squashed_0009_auto_20181116_2316')
    ]

    operations = [
        migrations.AlterModelOptions(
            name='registriesapplication',
            options={'ordering': ['primary_certificate_no'], 'verbose_name_plural': 'Applications'},
        ),
        # The Alter below, is to resolve a squash related circular dependancy issue.
        # Be aware, that as of writing this comment, the key introduced below already exists on the
        # production database. Re-running this migration step will result in an error.
        migrations.AlterField(
            model_name='organization',
            name='province_state',
            field=models.ForeignKey(db_column='province_state_code', on_delete=django.db.models.deletion.PROTECT, related_name='companies', to='gwells.ProvinceStateCode', verbose_name='Province/State'),
        )
    ]
