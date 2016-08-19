# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-19 19:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Geography',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('minimum', models.CharField(max_length=3)),
                ('maximum', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('id', models.CharField(max_length=4, primary_key=True, serialize=False)),
                ('name', models.CharField(default='Unnamed', max_length=64)),
                ('location', models.CharField(max_length=3)),
                ('description', models.TextField(blank=True, default='')),
                ('lat', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('lng', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('signage', models.CharField(default='Undecided', max_length=20)),
                ('shelter', models.CharField(default='Undecided', max_length=20)),
                ('operating', models.DateField(blank=True, null=True)),
                ('speed', models.IntegerField(default=25)),
                ('available', models.IntegerField(default=2)),
                ('geography', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stop.Geography')),
            ],
        ),
    ]
