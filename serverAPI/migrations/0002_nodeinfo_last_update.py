# Generated by Django 4.0.3 on 2022-12-16 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('serverAPI', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='nodeinfo',
            name='last_update',
            field=models.IntegerField(default=0),
        ),
    ]