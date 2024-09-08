# Generated by Django 5.0.4 on 2024-09-08 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicalcertificaterequest',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Issued', 'Issued'), ('Denied', 'Denied')], default='Pending', max_length=12),
        ),
    ]