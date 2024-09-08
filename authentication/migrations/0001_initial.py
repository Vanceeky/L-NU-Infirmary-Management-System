# Generated by Django 5.0.4 on 2024-09-08 18:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id_number', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('contact_number', models.CharField(max_length=11)),
                ('age', models.CharField(blank=True, max_length=3, null=True)),
                ('gender', models.CharField(max_length=6)),
                ('category', models.CharField(max_length=8)),
                ('designation', models.CharField(max_length=100)),
                ('proof', models.FileField(upload_to='proofs/')),
                ('avatar', models.ImageField(blank=True, default='/team-3.jpg', null=True, upload_to='avatars/')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
