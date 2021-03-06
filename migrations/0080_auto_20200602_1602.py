# Generated by Django 2.2.10 on 2020-06-02 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0079_auto_20200403_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admission',
            name='use_address_for_billing',
            field=models.BooleanField(default=True, verbose_name='Use address for billing'),
        ),
        migrations.AlterField(
            model_name='admission',
            name='use_address_for_post',
            field=models.BooleanField(default=True, verbose_name='Use address for post'),
        ),
    ]
