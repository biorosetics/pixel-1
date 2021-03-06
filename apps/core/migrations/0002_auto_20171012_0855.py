# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-12 08:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='label',
            field=models.CharField(default='', help_text='The name of the tag, without ancestors', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tag',
            name='level',
            field=models.IntegerField(default=1, help_text='The level of the tag in the tree'),
        ),
        migrations.AddField(
            model_name='tag',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='core.Tag'),
        ),
        migrations.AddField(
            model_name='tag',
            name='path',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='analysis',
            name='tags',
            field=tagulous.models.fields.TagField(_set_tag_meta=True, force_lowercase=True, help_text='Enter a comma-separated tag string', to='core.Tag', tree=True),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='tags',
            field=tagulous.models.fields.TagField(_set_tag_meta=True, force_lowercase=True, help_text='Enter a comma-separated tag string', to='core.Tag', tree=True),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('slug', 'parent')]),
        ),
    ]
