# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-03-20 19:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0441_auto_20190320_1906'),
        ('continuing_education', '0051_auto_20190312_1438'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='persontraining',
            unique_together=set([('person', 'training')]),
        ),
    ]
