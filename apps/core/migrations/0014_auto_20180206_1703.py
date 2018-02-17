# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-06 17:03
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20180122_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='pixelset',
            name='cached_omics_areas',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=[], size=None),
        ),
        migrations.AddField(
            model_name='pixelset',
            name='cached_omics_unit_types',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=[], size=None),
        ),
        migrations.AddField(
            model_name='pixelset',
            name='cached_species',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=[], size=None),
        ),
    ]