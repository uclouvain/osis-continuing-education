# Generated by Django 2.2.10 on 2020-03-16 14:59

from django.db import migrations


PERMISSIONS_TO_DELETE = [
    {"codename": "view_address", "content_type__model": "address"},
    {"codename": "delete_address", "content_type__model": "address"},
    {"codename": "change_address", "content_type__model": "address"},
    {"codename": "add_address", "content_type__model": "address"},
    {"codename": "add_admission", "content_type__model": 'admission'},
    {"codename": "delete_admission", "content_type__model": 'admission'},
    {"codename": "can_access_admission", "content_type__model": 'admission'},
    {"codename": "can_validate_registration", "content_type__model": 'admission'},
    {"codename": "can_create_json", "content_type__model": 'admission'},
    {"codename": "can_edit_received_file_field", "content_type__model": 'admission'},
    {"codename": "add_admissionfile", "content_type__model": "admissionfile"},
    {"codename": "change_admissionfile", "content_type__model": "admissionfile"},
    {"codename": "delete_admissionfile", "content_type__model": "admissionfile"},
    {"codename": "view_admissionfile", "content_type__model": "admissionfile"},
    {"codename": "add_continuingeducationperson", "content_type__model": "continuingeducationperson"},
    {"codename": "change_continuingeducationperson", "content_type__model": "continuingeducationperson"},
    {"codename": "delete_continuingeducationperson", "content_type__model": "continuingeducationperson"},
    {"codename": "view_continuingeducationperson", "content_type__model": "continuingeducationperson"},
    {"codename": "add_continuingeducationtraining", "content_type__model": "continuingeducationtraining"},
    {"codename": "change_continuingeducationtraining", "content_type__model": "continuingeducationtraining"},
    {"codename": "delete_continuingeducationtraining", "content_type__model": "continuingeducationtraining"},
    {"codename": "view_continuingeducationtraining", "content_type__model": "continuingeducationtraining"},
    {"codename": "add_persontraining", "content_type__model": "persontraining"},
    {"codename": "view_persontraining", "content_type__model": "persontraining"},
    {"codename": "delete_persontraining", "content_type__model": "persontraining"},
    {"codename": "change_persontraining", "content_type__model": "persontraining"},
    {"codename": "add_prospect", "content_type__model": "prospect"},
    {"codename": "change_prospect", "content_type__model": "prospect"},
    {"codename": "delete_prospect", "content_type__model": "prospect"},
    {"codename": "view_prospect", "content_type__model": "prospect"},
]


def remove_unused_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    db_alias = schema_editor.connection.alias

    for permission in PERMISSIONS_TO_DELETE:
        Permission.objects.using(db_alias).filter(
            content_type__app_label="continuing_education",
            **permission
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0076_auto_20200316_1133'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'default_permissions': []},
        ),
        migrations.AlterModelOptions(
            name='admission',
            options={'default_permissions': ['view', 'change'], 'ordering': ('formation', 'person_information'), 'permissions': (('validate_registration', 'Validate IUFC registration file'), ('change_received_file_state', 'Change received file state'))},
        ),
        migrations.AlterModelOptions(
            name='admissionfile',
            options={'default_permissions': []},
        ),
        migrations.AlterModelOptions(
            name='continuingeducationperson',
            options={'default_permissions': [], 'ordering': ('person__last_name', 'person__first_name')},
        ),
        migrations.AlterModelOptions(
            name='continuingeducationtraining',
            options={'default_permissions': [], 'ordering': ('education_group',)},
        ),
        migrations.AlterModelOptions(
            name='persontraining',
            options={'default_permissions': []},
        ),
        migrations.AlterModelOptions(
            name='prospect',
            options={'default_permissions': []},
        ),
        migrations.RunPython(
            remove_unused_permissions,
            migrations.RunPython.noop
        )
    ]