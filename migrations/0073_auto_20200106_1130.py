# Generated by Django 2.2.5 on 2020-01-06 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0072_auto_20191014_1333'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='admission',
            options={'ordering': ('formation', 'person_information'), 'permissions': (('can_access_admission', 'Can consult IUFC admission information'), ('can_validate_registration', 'Can validate IUFC registration file'), ('can_create_json', 'Can create JSON file'), ('can_edit_received_file_field', 'Can edit received file field'))},
        ),
        migrations.AlterModelOptions(
            name='continuingeducationperson',
            options={'ordering': ('person__last_name', 'person__first_name')},
        ),
        migrations.AlterModelOptions(
            name='continuingeducationtraining',
            options={'ordering': ('education_group__educationgroupyear__acronym',)},
        ),
        migrations.AlterField(
            model_name='admission',
            name='state',
            field=models.CharField(blank=True, choices=[('Accepted', 'Accepted'), ('Accepted (no registration required)', 'Accepted (no registration required)'), ('Rejected', 'Rejected'), ('Waiting', 'Waiting'), ('Draft', 'Draft'), ('Submitted', 'Submitted'), ('Registration submitted', 'Registration submitted'), ('Validated', 'Validated'), ('Cancelled', 'Cancelled'), ('Cancelled (no registration required)', 'Cancelled (no registration required)')], default='Draft', max_length=50, verbose_name='State'),
        ),
    ]
