# Generated by Django 4.2.6 on 2023-11-29 11:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('doctor_id', models.AutoField(primary_key=True, serialize=False)),
                ('age', models.IntegerField()),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10)),
                ('experince', models.IntegerField()),
                ('languages', models.CharField(max_length=25)),
                ('mobile_number', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('schedule', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('prescription_id', models.IntegerField()),
                ('patient_id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.RenameField(
            model_name='patient',
            old_name='Address',
            new_name='address',
        ),
        migrations.RenameField(
            model_name='patient',
            old_name='Blood_group',
            new_name='blood_group',
        ),
        migrations.RenameField(
            model_name='patient',
            old_name='Date_of_birth',
            new_name='date_of_birth',
        ),
        migrations.RenameField(
            model_name='patient',
            old_name='Email_id',
            new_name='email_id',
        ),
        migrations.RenameField(
            model_name='patient',
            old_name='Gender',
            new_name='gender',
        ),
        migrations.RenameField(
            model_name='patient',
            old_name='Mobile_number',
            new_name='mobile_number',
        ),
        migrations.RenameField(
            model_name='patient',
            old_name='Name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='patient',
            old_name='Patient_id',
            new_name='patient_id',
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('appointment_id', models.AutoField(primary_key=True, serialize=False)),
                ('specialization', models.CharField(max_length=50)),
                ('doctor_name', models.CharField(max_length=50)),
                ('consultation_fee', models.IntegerField()),
                ('date', models.DateField()),
                ('Patient_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clinic.patient')),
            ],
        ),
    ]