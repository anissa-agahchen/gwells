# Generated by Django 2.1.7 on 2019-03-01 01:00

import datetime
from django.conf import settings
from django.db import migrations, models
from django.core.exceptions import ObjectDoesNotExist
import django.db.models.deletion
import uuid


def update_registries_application_status(apps, schema_editor):
    RegistriesApplicationStatus = apps.get_model(
        'registries', 'RegistriesApplicationStatus')
    RegistriesApplication = apps.get_model(
        'registries', 'RegistriesApplication')
    for application in RegistriesApplication.objects.all():
        pending = RegistriesApplicationStatus\
            .objects.filter(application=application,
                            status__registries_application_status_code='P').first()
        if pending:
            application.current_status = pending.status
            application.application_recieved_date = pending.effective_date
        approved = RegistriesApplicationStatus\
            .objects.filter(application=application,
                            status__registries_application_status_code='A').first()
        if approved:
            application.current_status = approved.status
            application.application_outcome_date = approved.effective_date
            application.application_outcome_notification_date = approved.notified_date
        not_approved = RegistriesApplicationStatus\
            .objects.filter(application=application,
                            status__registries_application_status_code='NA').first()
        if not_approved:
            application.current_status = approved.status
            application.application_outcome_date = not_approved.effective_date
            application.application_outcome_notification_date = not_approved.notified_date

        incomplete = RegistriesApplicationStatus\
            .objects.filter(application=application,
                            status__registries_application_status_code='I').first()
        if incomplete:
            application.current_status = incomplete.status
            application.application_outcome_date = incomplete.effective_date
            application.application_outcome_notification_date = incomplete.notified_date
        application.save()


def revert_registries_application_status(apps, schema_editor):
    RegistriesApplication = apps.get_model(
        'registries', 'RegistriesApplication')
    for application in RegistriesApplication.objects.all():
        application.current_status = None
        application.application_recieved_date = None
        application.application_outcome_date = None
        application.application_outcome_notification_date = None
        application.save()


def insert_remove_reasons(apps, schema_editor):
    data = {
        'FAILTM': {
            'description': 'Fails to maintain a requirement for registration',
            'display_order': 1
        },
        'NLACT': {
            'description': 'No longer actively working in Canada',
            'display_order': 2
        },
        'NMEET': {
            'description': 'Fails to meet a requirement for registration',
            'display_order': 3
        }
    }
    RegistriesRemovalReason = apps.get_model('registries', 'RegistriesRemovalReason')

    for (key, value) in data.items():
        RegistriesRemovalReason.objects.update_or_create(code=key, defaults=value)


def revert_remove_reasons(apps, schema_editor):
    # We don't need to do anything on revert
    pass


def update_application_approved_status(apps, schema_editor):
    ApplicationStatusCode = apps.get_model('registries', 'ApplicationStatusCode')
    try:
        code = ApplicationStatusCode.objects.get(code='A')
        code.description = 'Registered'
        code.save()
    except ObjectDoesNotExist as e:
        # On an empty database, this records may not exist (it will be loaded with fixtures)
        # No-one cares anymore (all production data has been migrated) so we don't even
        # bother logging it.
        pass


def revert_application_approved_status(apps, schema_editor):
    ApplicationStatusCode = apps.get_model('registries', 'ApplicationStatusCode')
    try:
        code = ApplicationStatusCode.objects.get(code='A')
        code.description = 'Approved'
        code.save()
    except ObjectDoesNotExist as e:
        # On an empty database, this records may not exist (it will be loaded with fixtures)
        logger.debug('ApplicationStatusCode with code \'A\' not found.'
                     'This is expected on an empty database.')


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='vw_well_class',
            fields=[
                ('subactivity', models.CharField(editable=False, max_length=10, primary_key=True, serialize=False)),
                ('class_desc', models.CharField(max_length=100)),
                ('class_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Registries Well Class',
                'verbose_name_plural': 'Registries Well Classes',
                'db_table': 'vw_well_class',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AccreditedCertificateCode',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('acc_cert_guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Accredited Certificate UUID')),
                ('name', models.CharField(editable=False, max_length=100, verbose_name='Certificate Name')),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Accredited Certificates',
                'db_table': 'registries_accredited_certificate_code',
                'ordering': ['registries_activity', 'cert_auth'],
            },
        ),
        migrations.CreateModel(
            name='ActivityCode',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('registries_activity_code', models.CharField(editable=False, max_length=10, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=100)),
                ('display_order', models.PositiveIntegerField()),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Activity codes',
                'db_table': 'registries_activity_code',
                'ordering': ['display_order', 'description'],
            },
        ),
        migrations.CreateModel(
            name='ApplicationStatusCode',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('registries_application_status_code', models.CharField(editable=False, max_length=10, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=100)),
                ('display_order', models.PositiveIntegerField()),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Application Status Codes',
                'db_table': 'registries_application_status_code',
                'ordering': ['display_order', 'description'],
            },
        ),
        migrations.CreateModel(
            name='CertifyingAuthorityCode',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('cert_auth_code', models.CharField(editable=False, max_length=50, primary_key=True, serialize=False, verbose_name='Certifying Authority Name')),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Certifying Authorities',
                'db_table': 'registries_certifying_authority_code',
                'ordering': ['cert_auth_code'],
            },
        ),
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('contact_detail_guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Contact At UUID')),
                ('contact_tel', models.CharField(blank=True, max_length=15, null=True, verbose_name='Contact telephone number')),
                ('contact_cell', models.CharField(blank=True, max_length=15, null=True, verbose_name='Contact cell number')),
                ('contact_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email adddress')),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Contact Information',
                'db_table': 'registries_contact_detail',
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('org_guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Organization UUID')),
                ('name', models.CharField(max_length=200)),
                ('street_address', models.CharField(max_length=100, null=True, verbose_name='Street Address')),
                ('city', models.CharField(max_length=50, null=True, verbose_name='Town/City')),
                ('postal_code', models.CharField(max_length=10, null=True, verbose_name='Postal Code')),
                ('main_tel', models.CharField(max_length=15, null=True, verbose_name='Telephone number')),
                ('fax_tel', models.CharField(max_length=15, null=True, verbose_name='Fax number')),
                ('website_url', models.URLField(null=True, verbose_name='Website')),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
                ('province_state', models.IntegerField(db_column='province_state_code', null=True)),
            ],
            options={
                'verbose_name_plural': 'Organizations',
                'db_table': 'registries_organization',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('person_guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Person UUID')),
                ('first_name', models.CharField(max_length=100)),
                ('surname', models.CharField(max_length=100)),
                ('well_driller_orcs_no', models.CharField(blank=True, max_length=25, null=True, verbose_name='ORCS File # reference (in context of Well Driller).')),
                ('pump_installer_orcs_no', models.CharField(blank=True, max_length=25, null=True, verbose_name='ORCS File # reference (in context of Pump Installer).')),
                ('contact_tel', models.CharField(blank=True, max_length=15, null=True, verbose_name='Contact telephone number')),
                ('contact_cell', models.CharField(blank=True, max_length=15, null=True, verbose_name='Contact cell number')),
                ('contact_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email address')),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'People',
                'db_table': 'registries_person',
                'ordering': ['first_name', 'surname'],
            },
        ),
        migrations.CreateModel(
            name='PersonNote',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('person_note_guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Person note UUID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField(max_length=2000)),
                ('author', models.ForeignKey(db_column='user_guid', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Author reference')),
                ('person', models.ForeignKey(db_column='person_guid', on_delete=django.db.models.deletion.PROTECT, related_name='notes', to='registries.Person', verbose_name='Person reference')),
            ],
            options={
                'db_table': 'registries_person_note',
            },
        ),
        migrations.CreateModel(
            name='Qualification',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('registries_well_qualification_guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Qualification / Well Class UUID')),
                ('display_order', models.PositiveIntegerField()),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Qualification codes',
                'db_table': 'registries_well_qualification',
                'ordering': ['subactivity', 'display_order'],
            },
        ),
        migrations.CreateModel(
            name='Register',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('register_guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Register UUID')),
                ('registration_no', models.CharField(blank=True, max_length=15, null=True)),
                ('registration_date', models.DateField(blank=True, null=True)),
                ('register_removal_date', models.DateField(blank=True, null=True, verbose_name='Date of Removal from Register')),
                ('organization', models.ForeignKey(blank=True, db_column='organization_guid', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='registrations', to='registries.Organization')),
                ('person', models.ForeignKey(db_column='person_guid', on_delete=django.db.models.deletion.PROTECT, related_name='registrations', to='registries.Person')),
            ],
            options={
                'verbose_name_plural': 'Registrations',
                'db_table': 'registries_register',
            },
        ),
        migrations.CreateModel(
            name='Register_Note',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('register_note_guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Register Node UUID')),
                ('notes', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Registrar notes, for internal use only.')),
                ('registration', models.ForeignKey(db_column='register_guid', on_delete=django.db.models.deletion.PROTECT, related_name='notes', to='registries.Register', verbose_name='Register Reference')),
            ],
            options={
                'verbose_name_plural': 'Registrar Notes',
                'db_table': 'registries_register_note',
            },
        ),
        migrations.CreateModel(
            name='RegistriesApplication',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('application_guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Register Application UUID')),
                ('file_no', models.CharField(blank=True, max_length=25, null=True, verbose_name='ORCS File # reference.')),
                ('over19_ind', models.BooleanField(default=True)),
                ('registrar_notes', models.CharField(blank=True, max_length=255, null=True, verbose_name='Registrar notes, for internal use only.')),
                ('reason_denied', models.CharField(blank=True, max_length=255, null=True, verbose_name='Free form text explaining reason for denial.')),
                ('primary_certificate_no', models.CharField(max_length=50)),
                ('primary_certificate', models.ForeignKey(blank=True, db_column='acc_cert_guid', null=True, on_delete=django.db.models.deletion.PROTECT, to='registries.AccreditedCertificateCode', verbose_name='Certificate')),
                ('registration', models.ForeignKey(db_column='register_guid', on_delete=django.db.models.deletion.PROTECT, related_name='applications', to='registries.Register', verbose_name='Person Reference')),
            ],
            options={
                'verbose_name_plural': 'Applications',
                'db_table': 'registries_application',
            },
        ),
        migrations.CreateModel(
            name='RegistriesApplicationStatus',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('application_status_guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Register Application Status UUID')),
                ('notified_date', models.DateField(blank=True, default=datetime.date.today, null=True)),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
                ('application', models.ForeignKey(db_column='application_guid', on_delete=django.db.models.deletion.CASCADE, related_name='status_set', to='registries.RegistriesApplication', verbose_name='Application Reference')),
                ('status', models.ForeignKey(db_column='registries_application_status_code', on_delete=django.db.models.deletion.PROTECT, to='registries.ApplicationStatusCode', verbose_name='Application Status Code Reference')),
            ],
            options={
                'verbose_name_plural': 'Application status',
                'db_table': 'registries_application_status',
                'ordering': ['application', 'effective_date'],
            },
        ),
        migrations.CreateModel(
            name='RegistriesRemovalReason',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('registries_removal_reason_code', models.CharField(editable=False, max_length=10, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=100)),
                ('display_order', models.PositiveIntegerField()),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Registry Removal Reasons',
                'db_table': 'registries_removal_reason_code',
                'ordering': ['display_order', 'description'],
            },
        ),
        migrations.CreateModel(
            name='RegistriesStatusCode',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('registries_status_code', models.CharField(editable=False, max_length=10, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=100)),
                ('display_order', models.PositiveIntegerField()),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Registry Status Codes',
                'db_table': 'registries_status_code',
                'ordering': ['display_order', 'description'],
            },
        ),
        migrations.CreateModel(
            name='SubactivityCode',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('registries_subactivity_code', models.CharField(editable=False, max_length=10, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=100)),
                ('display_order', models.PositiveIntegerField()),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
                ('registries_activity', models.ForeignKey(db_column='registries_activity_code', on_delete=django.db.models.deletion.PROTECT, to='registries.ActivityCode')),
            ],
            options={
                'verbose_name_plural': 'Subactivity codes',
                'db_table': 'registries_subactivity_code',
                'ordering': ['display_order', 'description'],
            },
        ),
        migrations.CreateModel(
            name='WellClassCode',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('registries_well_class_code', models.CharField(editable=False, max_length=10, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=100)),
                ('display_order', models.PositiveIntegerField()),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Well Classes',
                'db_table': 'registries_well_class_code',
                'ordering': ['display_order', 'description'],
            },
        ),
        migrations.AddField(
            model_name='registriesapplication',
            name='subactivity',
            field=models.ForeignKey(db_column='registries_subactivity_code', on_delete=django.db.models.deletion.PROTECT, related_name='applications', to='registries.SubactivityCode'),
        ),
        migrations.AddField(
            model_name='register',
            name='register_removal_reason',
            field=models.ForeignKey(blank=True, db_column='registries_removal_reason_code', null=True, on_delete=django.db.models.deletion.PROTECT, to='registries.RegistriesRemovalReason', verbose_name='Removal Reason'),
        ),
        migrations.AddField(
            model_name='register',
            name='registries_activity',
            field=models.ForeignKey(db_column='registries_activity_code', on_delete=django.db.models.deletion.PROTECT, to='registries.ActivityCode'),
        ),
        migrations.AddField(
            model_name='register',
            name='status',
            field=models.ForeignKey(blank=True, db_column='registries_status_code', null=True, on_delete=django.db.models.deletion.PROTECT, to='registries.RegistriesStatusCode', verbose_name='Register Entry Status'),
        ),
        migrations.AddField(
            model_name='qualification',
            name='subactivity',
            field=models.ForeignKey(db_column='registries_subactivity_code', on_delete=django.db.models.deletion.PROTECT, related_name='qualification_set', to='registries.SubactivityCode'),
        ),
        migrations.AddField(
            model_name='qualification',
            name='well_class',
            field=models.ForeignKey(db_column='registries_well_class_code', on_delete=django.db.models.deletion.PROTECT, to='registries.WellClassCode'),
        ),
        migrations.AddField(
            model_name='contactinfo',
            name='person',
            field=models.ForeignKey(db_column='person_guid', on_delete=django.db.models.deletion.PROTECT, related_name='contact_info', to='registries.Person', verbose_name='Person Reference'),
        ),
        migrations.AddField(
            model_name='accreditedcertificatecode',
            name='cert_auth',
            field=models.ForeignKey(db_column='cert_auth_code', on_delete=django.db.models.deletion.PROTECT, to='registries.CertifyingAuthorityCode'),
        ),
        migrations.AddField(
            model_name='accreditedcertificatecode',
            name='registries_activity',
            field=models.ForeignKey(db_column='registries_activity_code', on_delete=django.db.models.deletion.PROTECT, to='registries.ActivityCode'),
        ),
        migrations.CreateModel(
            name='OrganizationNote',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('org_note_guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Company note UUID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField(max_length=2000)),
                ('author', models.ForeignKey(db_column='user_guid', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Author reference')),
            ],
            options={
                'db_table': 'registries_organization_note',
            },
        ),
        migrations.AddField(
            model_name='organization',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email adddress'),
        ),
        migrations.AddField(
            model_name='organizationnote',
            name='organization',
            field=models.ForeignKey(db_column='org_guid', on_delete=django.db.models.deletion.PROTECT, related_name='notes', to='registries.Organization', verbose_name='Company reference'),
        ),
        migrations.CreateModel(
            name='ProofOfAgeCode',
            fields=[
                ('create_user', models.CharField(max_length=60)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('update_user', models.CharField(max_length=60, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('registries_proof_of_age_code', models.CharField(editable=False, max_length=10, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=100)),
                ('display_order', models.PositiveIntegerField()),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('expired_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'ProofOfAgeCodes',
                'db_table': 'registries_proof_of_age_code',
                'ordering': ['display_order', 'description'],
            },
        ),
        migrations.RemoveField(
            model_name='registriesapplication',
            name='over19_ind',
        ),
        migrations.AddField(
            model_name='registriesapplication',
            name='proof_of_age',
            field=models.ForeignKey(db_column='registries_proof_of_age_code', null=True, on_delete=django.db.models.deletion.PROTECT, to='registries.ProofOfAgeCode', verbose_name='Proof of age.'),
        ),
        migrations.AddField(
            model_name='registriesapplication',
            name='application_outcome_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='registriesapplication',
            name='application_outcome_notification_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='registriesapplication',
            name='application_recieved_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='registriesapplication',
            name='current_status',
            field=models.ForeignKey(blank=True, db_column='registries_application_status_code', null=True, on_delete=django.db.models.deletion.PROTECT, to='registries.ApplicationStatusCode', verbose_name='Application Status Code Reference'),
        ),
        migrations.RunPython(
            code=update_registries_application_status,
            reverse_code=revert_registries_application_status),
        migrations.AddField(
            model_name='registriesapplication',
            name='removal_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='registriesapplication',
            name='removal_reason',
            field=models.ForeignKey(blank=True, db_column='registries_removal_reason_code', null=True, on_delete=django.db.models.deletion.PROTECT, to='registries.RegistriesRemovalReason', verbose_name='Removal Reason'),
        ),
        migrations.RenameField(
            model_name='proofofagecode',
            old_name='registries_proof_of_age_code',
            new_name='code',
        ),
        migrations.AlterField(
            model_name='proofofagecode',
            name='code',
            field=models.CharField(db_column='registries_proof_of_age_code', editable=False, max_length=10, primary_key=True, serialize=False),
        ),
        migrations.RenameField(
            model_name='applicationstatuscode',
            old_name='registries_application_status_code',
            new_name='code',
        ),
        migrations.AlterField(
            model_name='applicationstatuscode',
            name='code',
            field=models.CharField(db_column='registries_application_status_code', editable=False, max_length=10, primary_key=True, serialize=False),
        ),
        migrations.RenameField(
            model_name='registriesremovalreason',
            old_name='registries_removal_reason_code',
            new_name='code',
        ),
        migrations.AlterField(
            model_name='registriesremovalreason',
            name='code',
            field=models.CharField(db_column='registries_removal_reason_code', editable=False, max_length=10, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='organization',
            name='city',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Town/City'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='fax_tel',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Fax number'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='main_tel',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Telephone number'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='postal_code',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Postal Code'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='street_address',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Street Address'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='website_url',
            field=models.URLField(blank=True, null=True, verbose_name='Website'),
        ),
        migrations.RemoveField(
            model_name='registriesapplicationstatus',
            name='application',
        ),
        migrations.RemoveField(
            model_name='registriesapplicationstatus',
            name='status',
        ),
        migrations.RemoveField(
            model_name='register',
            name='register_removal_date',
        ),
        migrations.RemoveField(
            model_name='register',
            name='register_removal_reason',
        ),
        migrations.RemoveField(
            model_name='register',
            name='registration_date',
        ),
        migrations.RemoveField(
            model_name='register',
            name='status',
        ),
        migrations.DeleteModel(
            name='RegistriesApplicationStatus',
        ),
        migrations.DeleteModel(
            name='RegistriesStatusCode',
        ),
        migrations.RunPython(
            code=insert_remove_reasons,
            reverse_code=revert_remove_reasons),
        migrations.RunPython(
            code=update_application_approved_status,
            reverse_code=revert_application_approved_status,
        ),
        migrations.RemoveField(
            model_name='contactinfo',
            name='person',
        ),
        migrations.DeleteModel(
            name='ContactInfo',
        ),
    ]
