# Generated by Django 4.0.3 on 2022-12-13 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AreaInfo',
            fields=[
                ('chainID', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('bc_endpoint', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'area_info',
            },
        ),
        migrations.CreateModel(
            name='CarInfo',
            fields=[
                ('address', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'car_info',
            },
        ),
        migrations.CreateModel(
            name='NodeInfo',
            fields=[
                ('reg_time', models.DateTimeField()),
                ('address', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('private_key', models.CharField(max_length=255)),
                ('loc_x', models.IntegerField()),
                ('loc_y', models.IntegerField()),
                ('chain_id', models.CharField(max_length=255)),
                ('host', models.CharField(default='127.0.0.1:8000', max_length=255)),
                ('credit', models.FloatField(default=100)),
            ],
            options={
                'db_table': 'node_info',
            },
        ),
        migrations.CreateModel(
            name='SelfInfo',
            fields=[
                ('address', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('private_key', models.CharField(max_length=255)),
                ('current_round', models.PositiveIntegerField()),
                ('bc_port', models.CharField(max_length=5)),
            ],
            options={
                'db_table': 'self_info',
            },
        ),
        migrations.CreateModel(
            name='CheckPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chain_id', models.CharField(default='', max_length=255)),
                ('owner', models.CharField(max_length=255)),
                ('round', models.PositiveIntegerField()),
                ('result', models.PositiveIntegerField()),
            ],
            options={
                'db_table': 'checkpoint',
                'unique_together': {('chain_id', 'owner', 'round')},
            },
        ),
    ]
