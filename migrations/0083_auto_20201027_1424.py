# Generated by Django 2.2.10 on 2020-10-27 14:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('continuing_education', '0082_auto_20201013_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admission',
            name='id_card_number',
            field=models.CharField(blank=True, max_length=255, validators=[
                django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')],
                                   verbose_name='ID card number'),
        ),
        migrations.AlterField(
            model_name='admission',
            name='national_registry_number',
            field=models.CharField(blank=True, max_length=255, validators=[
                django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')],
                                   verbose_name='National registry number'),
        ),
        migrations.AlterField(
            model_name='admission',
            name='passport_number',
            field=models.CharField(blank=True, max_length=255, validators=[
                django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')],
                                   verbose_name='Passport number'),
        ),
    ]
