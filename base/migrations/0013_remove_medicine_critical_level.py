# Generated by Django 5.0.4 on 2024-10-06 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_medicine_medicinerestock_medicineusage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medicine',
            name='critical_level',
        ),
    ]