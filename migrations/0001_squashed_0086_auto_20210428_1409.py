# Generated by Django 2.2.13 on 2021-05-26 07:55

import continuing_education.models.file
import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import osis_common.utils.validators
import uuid


class Migration(migrations.Migration):
    replaces = [('continuing_education', '0001_initial'), ('continuing_education', '0002_auto_20180629_1139'),
                ('continuing_education', '0003_auto_20180723_1230'),
                ('continuing_education', '0004_auto_20180807_1205'),
                ('continuing_education', '0005_admission_formation_spreading'),
                ('continuing_education', '0006_auto_20180824_1714'),
                ('continuing_education', '0007_auto_20180830_1418'),
                ('continuing_education', '0008_auto_20180830_1654'),
                ('continuing_education', '0009_auto_20180831_1118'),
                ('continuing_education', '0010_auto_20180831_1500'),
                ('continuing_education', '0011_auto_20180904_1059'),
                ('continuing_education', '0012_auto_20180905_1154'),
                ('continuing_education', '0013_auto_20180905_1447'),
                ('continuing_education', '0014_auto_20180911_1045'), ('continuing_education', '0015_admission_address'),
                ('continuing_education', '0016_auto_20180911_1101'),
                ('continuing_education', '0017_auto_20180911_1529'),
                ('continuing_education', '0018_auto_20181004_0018'),
                ('continuing_education', '0019_auto_20181004_0041'),
                ('continuing_education', '0020_auto_20181004_0041'),
                ('continuing_education', '0021_add_state_constraint'),
                ('continuing_education', '0022_remove_state_constraint'),
                ('continuing_education', '0023_auto_20181017_1138'),
                ('continuing_education', '0024_auto_20181022_0951'), ('continuing_education', '0025_file'),
                ('continuing_education', '0026_translations'),
                ('continuing_education', '0027_admission_awareness_other'),
                ('continuing_education', '0028_auto_20181204_1422'),
                ('continuing_education', '0029_auto_20181212_1040'),
                ('continuing_education', '0030_admission_state_reason'),
                ('continuing_education', '0031_file_uploaded_by'), ('continuing_education', '0032_file_uuid'),
                ('continuing_education', '0033_auto_20190116_1518'),
                ('continuing_education', '0034_file_file_category'),
                ('continuing_education', '0035_auto_20190122_1308'),
                ('continuing_education', '0036_auto_20190124_0810'),
                ('continuing_education', '0037_admission_registration_state'),
                ('continuing_education', '0038_auto_20190124_1502'),
                ('continuing_education', '0039_auto_20190201_1104'),
                ('continuing_education', '0040_auto_20190201_1614'),
                ('continuing_education', '0041_auto_20190206_1458'),
                ('continuing_education', '0042_auto_20190214_1242'),
                ('continuing_education', '0043_admission_archived'),
                ('continuing_education', '0044_admission_registration_file_received'),
                ('continuing_education', '0045_prospect'), ('continuing_education', '0046_prospect_uuid'),
                ('continuing_education', '0047_admission_diploma_produced'),
                ('continuing_education', '0048_auto_20190304_1154'),
                ('continuing_education', '0049_auto_20190305_1329'),
                ('continuing_education', '0050_auto_20190305_1355'),
                ('continuing_education', '0051_auto_20190312_1438'),
                ('continuing_education', '0052_continuingeducationtraining_training_aid'),
                ('continuing_education', '0053_auto_20190325_1408'),
                ('continuing_education', '0054_auto_20190328_1409'),
                ('continuing_education', '0055_auto_20190404_1509'),
                ('continuing_education', '0056_auto_20190409_1508'),
                ('continuing_education', '0057_auto_20190412_0938'),
                ('continuing_education', '0058_auto_20190415_0822'),
                ('continuing_education', '0059_auto_20190415_0959'),
                ('continuing_education', '0060_auto_20190415_1127'),
                ('continuing_education', '0061_auto_20190425_1528'),
                ('continuing_education', '0062_auto_20190426_0941'),
                ('continuing_education', '0063_admission_condition_of_acceptance'),
                ('continuing_education', '0064_auto_20190508_1448'),
                ('continuing_education', '0065_auto_20190508_1521'),
                ('continuing_education', '0066_auto_20190513_1253'),
                ('continuing_education', '0067_continuingeducationtraining_postal_address'),
                ('continuing_education', '0068_admission_additional_information'),
                ('continuing_education', '0069_continuingeducationtraining_additional_information_label'),
                ('continuing_education', '0070_admission_comment'), ('continuing_education', '0071_auto_20191001_1658'),
                ('continuing_education', '0072_auto_20191014_1333'),
                ('continuing_education', '0073_auto_20200106_1130'),
                ('continuing_education', '0074_admission_academic_year'),
                ('continuing_education', '0075_auto_20200310_1232'),
                ('continuing_education', '0076_auto_20200316_1133'),
                ('continuing_education', '0077_auto_20200316_1459'),
                ('continuing_education', '0078_auto_20200320_1108'),
                ('continuing_education', '0079_auto_20200403_1117'),
                ('continuing_education', '0080_auto_20200602_1602'),
                ('continuing_education', '0081_auto_20201013_1024'),
                ('continuing_education', '0082_auto_20201013_1545'),
                ('continuing_education', '0083_auto_20201027_1424'),
                ('continuing_education', '0084_auto_20210127_1119'),
                ('continuing_education', '0085_auto_20210423_1545'),
                ('continuing_education', '0086_auto_20210428_1409')]

    initial = True

    dependencies = [
        ('base', '0583_auto_20210324_0954'),
        ('base', '0358_auto_20180921_1059'),
        ('reference', '0017_language_changed'),
        ('base', '0433_auto_20190305_1329'),
        ('base', '0342_auto_20180830_1605'),
        ('base', '0441_auto_20190325_0907'),
        ('base', '0497_auto_20200108_1213'),
        ('reference', '0020_domain_changed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(blank=True, max_length=255, verbose_name='Location')),
                ('postal_code', models.CharField(blank=True, max_length=20, verbose_name='Postal code')),
                ('city', models.CharField(blank=True, max_length=255, verbose_name='City')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='address_country', to='reference.Country', verbose_name='Country')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='ContinuingEducationPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('birth_date', models.DateField(blank=True, default=datetime.date(2000, 1, 1), verbose_name='Birth date')),
                ('birth_location', models.CharField(blank=True, max_length=255, verbose_name='Birth location')),
                ('birth_country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='birth_country', to='reference.Country', verbose_name='Birth country')),
                ('person', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='base.Person')),
            ],
            options={
                'abstract': False,
                'ordering': ('person__last_name', 'person__first_name'),
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='ContinuingEducationTraining',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('education_group', models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroup')),
                ('training_aid', models.BooleanField(default=False, verbose_name='Training aid')),
                ('send_notification_emails', models.BooleanField(default=True, verbose_name='Send notification emails')),
                ('alternate_notification_email_addresses', models.TextField(blank=True, default='', help_text='Comma-separated addresses - Leave empty if no address', verbose_name='Alternate notification email addresses')),
                ('postal_address', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='continuing_education.Address')),
                ('additional_information_label', models.TextField(blank=True, default='', help_text='Leave empty if training does not require additional information', verbose_name='Additional information label')),
                ('registration_required', models.BooleanField(default=True, verbose_name='Registration required')),
            ],
            options={
                'default_permissions': ['view', 'change'],
                'ordering': ('education_group',),
                'permissions': (('manage_all_trainings', 'Manage all continuing education trainings'), ('set_training_active', 'Set a continuing education training as active')),
            },
        ),
        migrations.CreateModel(
            name='Admission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motivation', models.TextField(blank=True, verbose_name='Motivation')),
                ('awareness_ucl_website', models.BooleanField(default=False, verbose_name='By UCLouvain website')),
                ('awareness_formation_website', models.BooleanField(default=False, verbose_name='By formation website')),
                ('awareness_press', models.BooleanField(default=False, verbose_name='By press')),
                ('awareness_facebook', models.BooleanField(default=False, verbose_name='By Facebook')),
                ('awareness_linkedin', models.BooleanField(default=False, verbose_name='By LinkedIn')),
                ('awareness_customized_mail', models.BooleanField(default=False, verbose_name='By customized mail')),
                ('awareness_emailing', models.BooleanField(default=False, verbose_name='By emailing')),
                ('state', models.CharField(blank=True, choices=[('Accepted', 'Accepted'), ('Accepted (no registration required)', 'Accepted (no registration required)'), ('Rejected', 'Rejected'), ('Waiting', 'Waiting'), ('Draft', 'Draft'), ('Submitted', 'Submitted'), ('Registration submitted', 'Registration submitted'), ('Validated', 'Validated'), ('Cancelled', 'Cancelled'), ('Cancelled (no registration required)', 'Cancelled (no registration required)')], default='Draft', max_length=50, verbose_name='State')),
                ('assessment_presented', models.BooleanField(default=False, verbose_name='Assessment presented')),
                ('assessment_succeeded', models.BooleanField(default=False, verbose_name='Assessment succeeded')),
                ('children_number', models.SmallIntegerField(blank=True, default=0, verbose_name='Children number')),
                ('company_number', models.CharField(blank=True, max_length=255, verbose_name='Company number')),
                ('head_office_name', models.CharField(blank=True, max_length=255, verbose_name='Head office name')),
                ('id_card_number', models.CharField(blank=True, max_length=255, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')], verbose_name='ID card number')),
                ('marital_status', models.CharField(blank=True, choices=[('SINGLE', 'Single'), ('MARRIED', 'Married'), ('WIDOWED', 'Widowed'), ('DIVORCED', 'Divorced'), ('SEPARATED', 'Separated'), ('LEGAL_COHABITANT', 'Legal cohabitant')], max_length=255, verbose_name='Marital status')),
                ('national_registry_number', models.CharField(blank=True, max_length=255, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.'), osis_common.utils.validators.belgium_national_register_number_validator], verbose_name='National registry number')),
                ('noma', models.CharField(blank=True, max_length=255, verbose_name='NOMA')),
                ('passport_number', models.CharField(blank=True, max_length=255, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')], verbose_name='Passport number')),
                ('payment_complete', models.BooleanField(default=False, verbose_name='Payment complete')),
                ('previous_noma', models.CharField(blank=True, max_length=255, verbose_name='Previous NOMA')),
                ('previous_ucl_registration', models.BooleanField(default=False, verbose_name='Previous uclouvain registration')),
                ('prior_experience_validation', models.BooleanField(default=False, verbose_name='Prior experience validation')),
                ('registration_type', models.CharField(blank=True, choices=[('PRIVATE', 'Private'), ('PROFESSIONAL', 'Professional')], max_length=50, verbose_name='Registration type')),
                ('residence_phone', models.CharField(blank=True, max_length=30, verbose_name='Residence phone')),
                ('sessions', models.CharField(blank=True, max_length=255, verbose_name='Sessions')),
                ('spouse_name', models.CharField(blank=True, max_length=255, verbose_name='Spouse name')),
                ('use_address_for_billing', models.BooleanField(default=True, verbose_name='Use address for billing')),
                ('use_address_for_post', models.BooleanField(default=True, verbose_name='Use address for post')),
                ('vat_number', models.CharField(blank=True, max_length=255, verbose_name='VAT number')),
                ('formation_spreading', models.BooleanField(default=False, verbose_name='Formation spreading')),
                ('formation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='continuing_education.ContinuingEducationTraining', verbose_name='Formation')),
                ('billing_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='billing_address', to='continuing_education.Address', verbose_name='Billing address')),
                ('residence_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='residence_address', to='continuing_education.Address', verbose_name='Residence address')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('person_information', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='continuing_education.ContinuingEducationPerson', verbose_name='Person information')),
                ('activity_sector', models.CharField(blank=True, choices=[('PRIVATE', 'Private'), ('PUBLIC', 'Public'), ('ASSOCIATIVE', 'Associative'), ('HEALTH', 'Health'), ('OTHER', 'Other')], max_length=50, verbose_name='Activity sector')),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='continuing_education.Address', verbose_name='Address')),
                ('citizenship', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='citizenship', to='reference.Country', verbose_name='Citizenship')),
                ('current_employer', models.CharField(blank=True, max_length=50, verbose_name='Current employer')),
                ('current_occupation', models.CharField(blank=True, max_length=50, verbose_name='Current occupation')),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='Email')),
                ('high_school_diploma', models.BooleanField(default=False, verbose_name='High school diploma')),
                ('high_school_graduation_year', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='High school graduation year')),
                ('last_degree_field', models.CharField(blank=True, max_length=50, verbose_name='Last degree field')),
                ('last_degree_graduation_year', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Last degree graduation year')),
                ('last_degree_institution', models.CharField(blank=True, max_length=50, verbose_name='Last degree institution')),
                ('last_degree_level', models.CharField(blank=True, max_length=50, verbose_name='Last degree level')),
                ('other_educational_background', models.TextField(blank=True, verbose_name='Other educational background')),
                ('past_professional_activities', models.TextField(blank=True, verbose_name='Past professional activities')),
                ('phone_mobile', models.CharField(blank=True, max_length=30, verbose_name='Mobile phone')),
                ('professional_status', models.CharField(blank=True, choices=[('EMPLOYEE', 'Employee'), ('SELF_EMPLOYED', 'Self employed'), ('JOB_SEEKER', 'Job seeker'), ('PUBLIC_SERVANT', 'Public servant'), ('OTHER', 'Other')], max_length=50, verbose_name='Professional status')),
                ('awareness_other', models.CharField(blank=True, max_length=100, verbose_name='Other')),
                ('state_reason', models.TextField(blank=True, verbose_name='State reason')),
                ('ucl_registration_complete', models.CharField(blank=True, choices=[('INIT_STATE', 'Initial state'), ('SENDED', 'Sended'), ('INSCRIT', 'Registered'), ('DEMANDE', 'On demand'), ('REJECTED', 'Rejected'), ('NON_RENSEIGNE', 'Uninformed'), ('CONDITION', 'Provisional'), ('ANNULATION_ETD', 'Cancellation (ETD)'), ('ANNULATION_UCL', 'Cancellation (UNIV)'), ('EXCLUSION', 'Exclusion'), ('CESSATION', 'Cessation'), ('DECES', 'Death'), ('ERREUR', 'Error'), ('INTENTION_ECHANGE', 'Register intention'), ('ANNULATION_ECHANGE', 'Intention cancellation'), ('REINSCRIPTION_WEB', 'Internet re-registration'), ('ANNULATION_IP', 'IP Cancellation'), ('REFUS', 'Refusal'), ('CYCLE', 'Cycle'), ('VALISE_CREDITS', 'Valued crédits')], default='INIT_STATE', max_length=50, verbose_name='UCLouvain registration complete')),
                ('archived', models.BooleanField(default=False, verbose_name='Archived')),
                ('registration_file_received', models.BooleanField(default=False, verbose_name='Registration file received')),
                ('diploma_produced', models.BooleanField(default=False, verbose_name='Diploma produced')),
                ('awareness_former_students', models.BooleanField(default=False, verbose_name='By former students')),
                ('awareness_friends', models.BooleanField(default=False, verbose_name='By friends')),
                ('awareness_moocs', models.BooleanField(default=False, verbose_name='By Moocs')),
                ('awareness_word_of_mouth', models.BooleanField(default=False, verbose_name='By word of mouth')),
                ('professional_personal_interests', models.TextField(blank=True, verbose_name='Professional and personal interests')),
                ('reduced_rates', models.BooleanField(default=False, verbose_name='Reduced rates')),
                ('spreading_payments', models.BooleanField(default=False, verbose_name='Spreading payments')),
                ('condition_of_acceptance', models.TextField(blank=True, verbose_name='Condition of acceptance')),
                ('additional_information', models.TextField(blank=True, verbose_name='Additional information')),
                ('comment', models.TextField(blank=True, max_length=500, null=True, verbose_name='Comment')),
                ('academic_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.AcademicYear', verbose_name='Academic year')),
                ('ucl_registration_error', models.CharField(blank=True, choices=[('IUFC_NO_ERROR', 'No error'), ('IUFC_NOM_TROP_LONG', 'Too long name'), ('IUFC_PRENOM_TROP_LONG', 'Too long first name'), ('IUFC_ADRESSE_TROP_LONGUE', 'Too long address'), ('IUFC_NOM_MANQUANT', 'Missing name'), ('IUFC_PRENOM_MANQUANT', 'Missing first name'), ('IUFC_ANNEE_MANQUANTE', 'Missing year'), ('IUFC_PROGRAMME_MANQUANT', 'Missing program'), ('IUFC_NATIONALITE_MANQUANTE', 'Missing citizenship'), ('IUFC_PAYS_NAISSANCE_MANQUANT', 'Missing birth country'), ('IUFC_INSCRIPTION_DEJA_TRAITEE', 'Registration already processed'), ('IUFC_CREATION_NOMA_ECHOUEE', 'NOMA creation failed'), ('IUFC_ERREUR_INCONNUE', 'Unknown error: please contact <a class="error_msg_link" href="https://uclouvain.be/fr/decouvrir/service-desk.html">Service Desk</a> for further help')], default='IUFC_NO_ERROR', max_length=50, null=True, verbose_name='UCLouvain registration error')),
            ],
            options={
                'permissions': (('validate_registration', 'Validate IUFC registration file'), ('change_received_file_state', 'Change received file state'), ('link_admission_to_academic_year', 'Link an admission to an academic year'), ('inject_admission_to_epc', 'Inject an admission to EPC'), ('mark_diploma_produced', 'Mark an admission diploma has been produced'), ('send_notification', 'Send a notification related to an admission'), ('archive_admission', 'Archive an admission'), ('export_admission', 'Export an admission into XLSX file'), ('cancel_admission', 'Cancel an admission')),
                'ordering': ('formation', 'person_information'),
                'default_permissions': ['view', 'change'],
            },
        ),
        migrations.CreateModel(
            name='ContinuingEducationManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='base.person')),
            ],
            options={
                'verbose_name': 'Continuing education manager',
                'verbose_name_plural': 'Continuing education managers',
            },
        ),
        migrations.CreateModel(
            name='ContinuingEducationStudentWorker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='base.person')),
            ],
            options={
                'verbose_name': 'Continuing education student worker',
                'verbose_name_plural': 'Continuing education student workers',
            },
        ),
        migrations.CreateModel(
            name='ContinuingEducationTrainingManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='base.person')),
                ('training', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='continuing_education.ContinuingEducationTraining')),
            ],
            options={
                'verbose_name': 'Continuing education training manager',
                'verbose_name_plural': 'Continuing education training managers',
                'default_permissions': ['view', 'add', 'delete'],
                'unique_together': {('person', 'training')},
            },
        ),
        migrations.AddField(
            model_name='continuingeducationtraining',
            name='managers',
            field=models.ManyToManyField(through='continuing_education.ContinuingEducationTrainingManager', to='base.Person'),
        ),
        migrations.CreateModel(
            name='Prospect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, verbose_name='Name')),
                ('first_name', models.CharField(blank=True, max_length=250, verbose_name='First name')),
                ('postal_code', models.CharField(blank=True, max_length=250, verbose_name='Postal code')),
                ('city', models.CharField(blank=True, max_length=50, verbose_name='City')),
                ('email', models.EmailField(max_length=255, verbose_name='Email')),
                ('phone_number', models.CharField(blank=True, max_length=30, verbose_name='Phone number')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('formation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='continuing_education.ContinuingEducationTraining', verbose_name='Formation')),
            ],
            options={
                'abstract': False,
                'default_permissions': ['view'],
                'permissions': (('export_prospect', 'Export a prospect into XLSX file'),),
            },
        ),
        migrations.CreateModel(
            name='AdmissionFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('path', models.FileField(upload_to=continuing_education.models.file.admission_directory_path, verbose_name='Path')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('size', models.IntegerField(null=True, verbose_name='Size')),
                ('admission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='continuing_education.Admission', verbose_name='Admission')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='base.Person', verbose_name='Uploaded by')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('file_category', models.CharField(choices=[('Document', 'Document'), ('Invoice', 'Invoice'), ('Participant', 'Participant')], default='Document', max_length=20)),
            ],
            options={
                'default_permissions': [],
            },
        ),
    ]
