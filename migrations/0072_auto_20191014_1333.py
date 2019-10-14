# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-10-14 13:33
from __future__ import unicode_literals

import continuing_education.models.file
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0071_auto_20191001_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='continuingeducationtraining',
            name='registration_required',
            field=models.BooleanField(default=True, verbose_name='Registration required'),
        ),
        migrations.AlterField(
            model_name='admissionfile',
            name='path',
            field=models.FileField(upload_to=continuing_education.models.file.admission_directory_path, verbose_name='Path'),
        ),
    ]
