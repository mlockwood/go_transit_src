# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-20 17:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rider', '0002_auto_20160913_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='count',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='entry',
            name='time',
            field=models.TimeField(default='12:00:00'),
        ),
    ]
