# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-01-21 11:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0034_file_file_category'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='File',
            new_name='AdmissionFile',
        ),
    ]
