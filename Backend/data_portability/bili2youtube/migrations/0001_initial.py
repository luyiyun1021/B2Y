# Generated by Django 4.2.6 on 2023-10-16 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserIDMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buid', models.CharField(max_length=100, unique=True, verbose_name='Bilibili User ID')),
                ('yuid', models.CharField(max_length=100, unique=True, verbose_name='YouTube User ID')),
            ],
        ),
        migrations.CreateModel(
            name='VideoIDMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bvid', models.CharField(max_length=100, unique=True, verbose_name='Bilibili Video ID')),
                ('yvid', models.CharField(max_length=100, unique=True, verbose_name='YouTube Video ID')),
            ],
        ),
    ]
