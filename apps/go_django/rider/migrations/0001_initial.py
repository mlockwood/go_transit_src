# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-19 19:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vehicle', '0001_initial'),
        ('user', '0001_initial'),
        ('stop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField()),
                ('count', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schedule', models.IntegerField()),
                ('login', models.DateTimeField()),
                ('start_mileage', models.IntegerField()),
                ('end_mileage', models.IntegerField()),
                ('logout', models.DateTimeField()),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.EndUser')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.Vehicle')),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='metadata',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rider.Metadata'),
        ),
        migrations.AddField(
            model_name='entry',
            name='off',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='off_stop', to='stop.Stop'),
        ),
        migrations.AddField(
            model_name='entry',
            name='on',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='on_stop', to='stop.Stop'),
        ),
        migrations.AlterUniqueTogether(
            name='entry',
            unique_together=set([('metadata', 'time', 'on', 'off')]),
        ),
    ]
