# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-04 14:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Fleet',
            fields=[
                ('id', models.CharField(max_length=12, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80)),
                ('description', models.TextField()),
                ('lat', models.DecimalField(decimal_places=6, max_digits=9)),
                ('lng', models.DecimalField(decimal_places=6, max_digits=9)),
                ('operating', models.DateField()),
                ('phone', phonenumber_field.modelfields.PhoneNumberField()),
                ('schedule', models.TextField(default='24 hours every day except holidays')),
            ],
        ),
        migrations.CreateModel(
            name='FleetAsset',
            fields=[
                ('id', models.CharField(max_length=12, primary_key=True, serialize=False)),
                ('asset_type', models.CharField(choices=[('P', 'Pump'), ('T', 'Toolkit'), ('V', 'Vest')], max_length=1)),
                ('fleet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleet.Fleet')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalFleetAsset',
            fields=[
                ('id', models.CharField(db_index=True, max_length=12)),
                ('asset_type', models.CharField(choices=[('P', 'Pump'), ('T', 'Toolkit'), ('V', 'Vest')], max_length=1)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('fleet', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='fleet.Fleet')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'history_date',
                'verbose_name': 'historical fleet asset',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
    ]
