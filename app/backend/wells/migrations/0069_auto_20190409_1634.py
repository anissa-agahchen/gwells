# Generated by Django 2.1.8 on 2019-04-09 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wells', '0068_merge_20190328_2059'),
        ('aquifers', '0018_auto_20190409_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitysubmission',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='aquiferlithologycode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='aquiferwell',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='bcgs_numbers',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='casing',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='casingcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='casingmaterialcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='coordinateacquisitioncode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='decommissiondescription',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='decommissionmaterialcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='decommissionmethodcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='developmentmethodcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='drillingcompany',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='drillingmethodcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='filterpackmaterialcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='filterpackmaterialsizecode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='groundelevationmethodcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='hydraulicproperty',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='intendedwaterusecode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='landdistrictcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='licencedstatuscode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='linermaterialcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='linerperforation',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='lithologydescription',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='ltsaowner',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='obswellstatuscode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='perforation',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='screen',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='surfacesealmaterialcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='surfacesealmethodcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='waterqualitycharacteristic',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='waterqualitycolour',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='well',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='wellclasscode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='wellpublicationstatuscode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='wellstatuscode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='wellsubclasscode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='wellyieldunitcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='yieldestimationmethodcode',
            name='update_user',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='well',
            name='aquifer',
            field=models.ForeignKey(blank=True, db_column='aquifer_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='aquifers.Aquifer', verbose_name='Aquifer ID Number'),
        ),
    ]
