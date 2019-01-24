# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-01-24 11:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0036_auto_20190124_0810'),
    ]

    operations = [
        migrations.AddField(
            model_name='admission',
            name='registration_state',
            field=models.CharField(blank=True, choices=[('Waiting', 'Waiting'), ('Accepted', 'Accepted')], default='Waiting', max_length=50, verbose_name='Registration state'),
        ),
    ]