# Generated by Django 2.1.8 on 2019-04-09 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registries', '0017_auto_20190326_1935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accreditedcertificatecode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='activitycode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='applicationstatuscode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='certifyingauthoritycode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='organization',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='organizationnote',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='person',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='personnote',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='proofofagecode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='qualification',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='register',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='register_note',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='registriesapplication',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='registriesremovalreason',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='subactivitycode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='wellclasscode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
    ]
