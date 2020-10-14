# Generated by Django 3.1.1 on 2020-10-13 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('continuing_education', '0080_auto_20200602_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admission',
            name='ucl_registration_error',
            field=models.CharField(blank=True, choices=[('IUFC_NO_ERROR', 'No error'), ('IUFC_NOM_TROP_LONG', 'Too long name'), ('IUFC_PRENOM_TROP_LONG', 'Too long first name'), ('IUFC_ADRESSE_TROP_LONGUE', 'Too long address'), ('IUFC_NOM_MANQUANT', 'Missing name'), ('IUFC_PRENOM_MANQUANT', 'Missing first name'), ('IUFC_ANNEE_MANQUANTE', 'Missing year'), ('IUFC_PROGRAMME_MANQUANT', 'Missing program'), ('IUFC_NATIONALITE_MANQUANTE', 'Missing citizenship'), ('IUFC_PAYS_NAISSANCE_MANQUANT', 'Missing birth country'), ('IUFC_INSCRIPTION_DEJA_TRAITEE', 'Registration already processed'), ('IUFC_CREATION_NOMA_ECHOUEE', 'NOMA creation failed'), ('IUFC_ERREUR_INCONNUE', 'Unknown error: please contact Service Desk for further help')], default='IUFC_NO_ERROR', max_length=50, null=True, verbose_name='UCLouvain registration error'),
        ),
    ]