# Generated by Django 4.2.6 on 2024-03-10 14:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0008_appointment_time_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='doctor_name',
            new_name='doctor_id',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='time',
        ),
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.date(2024, 3, 10), null=True),
        ),
    ]
