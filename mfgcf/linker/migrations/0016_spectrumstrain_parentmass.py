# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-10 12:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linker', '0015_auto_20171110_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='spectrumstrain',
            name='parentmass',
            field=models.FloatField(null=True),
        ),
    ]
