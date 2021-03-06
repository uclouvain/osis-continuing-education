# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-04-25 15:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0060_auto_20190415_1127'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='admission',
            options={'permissions': (('can_access_admission', 'Can consult IUFC admission information'), ('can_validate_registration', 'Can validate IUFC registration file'), ('can_create_json', 'Can create JSON file'), ('can_edit_received_file_field', 'Can edit received file field'))},
        ),
    ]
