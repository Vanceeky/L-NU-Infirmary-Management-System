# Generated by Django 5.0.4 on 2024-09-22 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_vaccination_dose'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vaccination',
            name='dose',
            field=models.CharField(choices=[('1st Dose / Booster', '1st Dose/Booster'), ('2nd Dose', '2nd Dose'), ('3rd Dose', '3rd Dose')], max_length=100),
        ),
    ]
