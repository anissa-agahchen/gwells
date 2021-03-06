# Generated by Django 2.1.8 on 2019-04-09 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aquifers', '0017_aquiferresourcesection_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aquifer',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='aquiferdemand',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='aquifermaterial',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='aquiferproductivity',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='aquiferresource',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='aquiferresourcesection',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='aquifersubtype',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='aquifervulnerabilitycode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='qualityconcern',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='wateruse',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
    ]
