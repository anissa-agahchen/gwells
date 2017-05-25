# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-24 16:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('gwells', '0011_auto_20170504_0957'),
    ]

    operations = [
        migrations.CreateModel(
            name='WellActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('street_address', models.CharField(blank=True, max_length=100)),
                ('city', models.CharField(blank=True, max_length=50)),
                ('lot', models.CharField(blank=True, max_length=10)),
                ('plan', models.CharField(blank=True, max_length=20)),
                ('district_lot', models.CharField(blank=True, max_length=20)),
                ('pid', models.PositiveIntegerField(blank=True, null=True)),
                ('identification_plate_number', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('well_tag_number', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('diameter', models.CharField(blank=True, max_length=9)),
                ('total_depth_drilled', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('finished_well_depth', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('well_yield', models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True)),
                ('land_district', models.ForeignKey(blank=True, db_column='gwells_land_district_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='gwells.LandDistrict')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='well',
            name='land_district',
        ),
        migrations.RemoveField(
            model_name='well',
            name='well_owner',
        ),
        migrations.RemoveField(
            model_name='well',
            name='well_yield_unit',
        ),
        migrations.RenameField(
            model_name='wellowner',
            old_name='street_address',
            new_name='mailing_address',
        ),
        migrations.DeleteModel(
            name='Well',
        ),
        migrations.AddField(
            model_name='wellactivity',
            name='well_owner',
            field=models.ForeignKey(blank=True, db_column='gwells_well_owner_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='gwells.WellOwner'),
        ),
        migrations.AddField(
            model_name='wellactivity',
            name='well_yield_unit',
            field=models.ForeignKey(blank=True, db_column='gwells_well_yield_unit_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='gwells.WellYieldUnit'),
        ),
    ]