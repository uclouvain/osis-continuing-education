# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-09-04 10:59
from __future__ import unicode_literals

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0010_auto_20180831_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admission',
            name='activity_sector',
            field=models.CharField(blank=True, choices=[('PRIVATE', 'private'), ('PUBLIC', 'public'), ('ASSOCIATIVE', 'associative'), ('HEALTH', 'health'), ('OTHER', 'other')], default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='billing_city',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='billing_location',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='billing_postal_code',
            field=models.CharField(blank=True, default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='birth_date',
            field=models.DateField(blank=True, default=datetime.datetime.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='birth_location',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='children_number',
            field=models.SmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='admission',
            name='city',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='company_number',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='courses_formula',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='current_employer',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='current_occupation',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='faculty',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='first_name',
            field=models.CharField(blank=True, db_index=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='formation_administrator',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='gender',
            field=models.CharField(blank=True, choices=[('F', 'female'), ('M', 'male')], default='F', max_length=1),
        ),
        migrations.AlterField(
            model_name='admission',
            name='head_office_name',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='high_school_graduation_year',
            field=models.DateField(blank=True, default=datetime.datetime.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='id_card_number',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='last_degree_field',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='last_degree_graduation_year',
            field=models.DateField(blank=True, default=datetime.datetime.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='last_degree_institution',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='last_degree_level',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='last_name',
            field=models.CharField(blank=True, db_index=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='location',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='marital_status',
            field=models.CharField(blank=True, choices=[('SINGLE', 'single'), ('MARRIED', 'married'), ('WIDOWED', 'widowed'), ('DIVORCED', 'divorced'), ('SEPARATED', 'separated'), ('LEGAL_COHABITANT', 'legal_cohabitant')], default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='motivation',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='national_registry_number',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='noma',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='other_educational_background',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='passport_number',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='past_professional_activities',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='phone_mobile',
            field=models.CharField(blank=True, default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='postal_code',
            field=models.CharField(blank=True, default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='previous_noma',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='professional_impact',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='professional_status',
            field=models.CharField(blank=True, choices=[('EMPLOYEE', 'employee'), ('SELF_EMPLOYED', 'self_employed'), ('JOB_SEEKER', 'job_seeker'), ('PUBLIC_SERVANT', 'public_servant'), ('OTHER', 'other')], default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='program_code',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='registration_type',
            field=models.CharField(blank=True, choices=[('PRIVATE', 'private'), ('PROFESSIONAL', 'professional')], default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='residence_city',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='residence_location',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='residence_phone',
            field=models.CharField(blank=True, default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='residence_postal_code',
            field=models.CharField(blank=True, default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='sessions',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='spouse_name',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='state',
            field=models.CharField(blank=True, choices=[('accepted', 'accepted'), ('rejected', 'rejected'), ('waiting', 'waiting')], default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='admission',
            name='vat_number',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
    ]
