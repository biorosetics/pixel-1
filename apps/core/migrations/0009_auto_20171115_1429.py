# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-15 14:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_pixelset'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pixel',
            name='analysis',
        ),
        migrations.AddField(
            model_name='pixel',
            name='pixel_set',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='pixels', related_query_name='pixel', to='core.PixelSet'),
            preserve_default=False,
        ),
    ]
