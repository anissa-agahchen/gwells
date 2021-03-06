# Generated by Django 2.1.3 on 2018-11-27 02:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wells', '0035_auto_20181130_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitysubmission',
            name='decommission_method',
            field=models.ForeignKey(blank=True, db_column='decommission_method_code', null=True, on_delete=django.db.models.deletion.PROTECT, to='wells.DecommissionMethodCode', verbose_name='Method of Decommission'),
        ),
        migrations.AlterField(
            model_name='productiondata',
            name='well_yield_unit',
            field=models.ForeignKey(blank=True, db_column='well_yield_unit_code', null=True, on_delete=django.db.models.deletion.PROTECT, to='wells.WellYieldUnitCode'),
        ),
        migrations.AlterField(
            model_name='well',
            name='aquifer',
            field=models.ForeignKey(blank=True, db_column='aquifer_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='aquifers.Aquifer', verbose_name='Aquifer ID Number'),
        ),
        migrations.AlterField(
            model_name='well',
            name='bcgs_id',
            field=models.ForeignKey(blank=True, db_column='bcgs_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='wells.BCGS_Numbers', verbose_name='BCGS Mapsheet Number'),
        ),
        migrations.AlterField(
            model_name='well',
            name='decommission_method',
            field=models.ForeignKey(blank=True, db_column='decommission_method_code', null='True', on_delete=django.db.models.deletion.PROTECT, to='wells.DecommissionMethodCode', verbose_name='Method of Decommission'),
        ),
        migrations.AlterField(
            model_name='well',
            name='observation_well_status',
            field=models.ForeignKey(blank=True, db_column='obs_well_status_code', null='True', on_delete=django.db.models.deletion.PROTECT, to='wells.ObsWellStatusCode', verbose_name='Observation Well Status'),
        ),
    ]
