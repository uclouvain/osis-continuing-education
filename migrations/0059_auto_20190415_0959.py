# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-04-15 09:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0058_auto_20190415_0822'),
    ]

    operations = [
        migrations.AddField(
            model_name='admission',
            name='reduced_rates',
            field=models.BooleanField(default=False, verbose_name='Reduced rates'),
        ),
        migrations.AddField(
            model_name='admission',
            name='spreading_payments',
            field=models.BooleanField(default=False, verbose_name='Spreading payments'),
        ),
    ]