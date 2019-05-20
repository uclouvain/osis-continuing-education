# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-05-20 11:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0066_auto_20190513_1253'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prospect',
            name='name',
        ),
        migrations.AddField(
            model_name='prospect',
            name='last_name',
            field=models.CharField(blank=True, max_length=250, verbose_name='Last name'),
        ),
    ]