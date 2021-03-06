# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-19 19:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fleet', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bike',
            fields=[
                ('id', models.CharField(max_length=12, primary_key=True, serialize=False)),
                ('serial_number', models.CharField(max_length=40)),
                ('low_step', models.BooleanField()),
                ('fleet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleet.Fleet')),
            ],
        ),
        migrations.CreateModel(
            name='BikeGPS',
            fields=[
                ('id', models.CharField(max_length=12, primary_key=True, serialize=False)),
                ('serial_number', models.CharField(max_length=40)),
                ('wi_mm', models.CharField(max_length=40)),
                ('bike', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='bike.Bike')),
            ],
        ),
        migrations.CreateModel(
            name='CheckInOut',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.CharField(choices=[('L', 'Long term check-out up to 30 days.'), ('M', 'Medium term check-out up to 72 hours.'), ('S', 'Short term check-out up to 12 hours.')], max_length=1)),
                ('check_out', models.DateTimeField(auto_now_add=True)),
                ('check_in', models.DateTimeField()),
                ('bike', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bike.Bike')),
                ('fleet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleet.Fleet')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalBike',
            fields=[
                ('id', models.CharField(db_index=True, max_length=12)),
                ('serial_number', models.CharField(max_length=40)),
                ('low_step', models.BooleanField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('fleet', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='fleet.Fleet')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical bike',
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
        migrations.CreateModel(
            name='HistoricalBikeGPS',
            fields=[
                ('id', models.CharField(db_index=True, max_length=12)),
                ('serial_number', models.CharField(max_length=40)),
                ('wi_mm', models.CharField(max_length=40)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('bike', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='bike.Bike')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical bike gps',
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
        migrations.CreateModel(
            name='HistoricalLock',
            fields=[
                ('id', models.CharField(db_index=True, max_length=12)),
                ('serial_number', models.CharField(max_length=40)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('bike', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='bike.Bike')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical lock',
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
        migrations.CreateModel(
            name='Lock',
            fields=[
                ('id', models.CharField(max_length=12, primary_key=True, serialize=False)),
                ('serial_number', models.CharField(max_length=40)),
                ('bike', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='bike.Bike')),
            ],
        ),
    ]
