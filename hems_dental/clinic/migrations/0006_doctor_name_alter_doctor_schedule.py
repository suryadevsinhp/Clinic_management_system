# Generated by Django 4.2.6 on 2023-12-12 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0005_alter_patient_blood_group_alter_patient_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='schedule',
            field=models.CharField(blank=True, max_length=25),
        ),
    ]
