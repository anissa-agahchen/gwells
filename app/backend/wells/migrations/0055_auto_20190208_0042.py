# Generated by Django 2.1.5 on 2019-02-08 00:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wells', '0054_well_publication_status_codes'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitysubmission',
            name='well_publication_status',
            field=models.ForeignKey(db_column='well_publication_status_code', default='Published',
                                    on_delete=django.db.models.deletion.CASCADE, to='wells.WellPublicationStatusCode',
                                    verbose_name='Well Publication Status'),
        ),
        migrations.AddField(
            model_name='well',
            name='well_publication_status',
            field=models.ForeignKey(db_column='well_publication_status_code', default='Published',
                                    on_delete=django.db.models.deletion.CASCADE, to='wells.WellPublicationStatusCode',
                                    verbose_name='Well Publication Status'),
        ),
    ]
