# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-03-04 15:37
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0049_auto_20190304_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='continuingeducationtraining',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
