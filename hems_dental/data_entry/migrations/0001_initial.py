# Generated by Django 4.2.6 on 2023-11-23 04:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='All_entries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('general', models.CharField(max_length=60)),
                ('doctor_name', models.CharField(max_length=60)),
                ('patient_name', models.CharField(max_length=60)),
                ('entry_time', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='data_entered',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor_details', models.CharField(max_length=200)),
                ('patient_details', models.CharField(max_length=200)),
                ('person_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_entry.all_entries')),
            ],
        ),
    ]
