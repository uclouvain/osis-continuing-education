# Generated by Django 2.2.5 on 2020-01-21 09:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0497_auto_20200108_1213'),
        ('continuing_education', '0073_auto_20200106_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='admission',
            name='academic_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.AcademicYear', verbose_name='Academic year'),
        ),
    ]
