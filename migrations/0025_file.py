# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-09 09:44
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import continuing_education.models.file


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0024_auto_20181022_0951'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('path', models.FileField(upload_to=continuing_education.models.file.admission_directory_path, verbose_name='path')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('size', models.IntegerField(null=True, verbose_name='size')),
                ('admission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='continuing_education.Admission', verbose_name='admision')),
            ],
        ),
    ]
