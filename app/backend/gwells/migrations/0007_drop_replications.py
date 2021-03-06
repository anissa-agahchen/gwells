# Generated by Django 2.1.8 on 2019-04-04 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gwells', '0006_auto_20190326_1914'),
    ]

    operations = [
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS populate_xform(boolean);"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS migrate_bcgs()"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS populate_well()"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS migrate_screens()"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS migrate_casings()"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS migrate_drilling_methods()"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS migrate_well_water_quality()"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS migrate_development_methods()"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS migrate_perforations()"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS migrate_aquifers()"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS migrate_lithology()"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS db_replicate_step1(boolean)"
        ),
        migrations.RunSQL(
            "DROP FUNCTION IF EXISTS db_replicate_step2()"
        )
    ]
