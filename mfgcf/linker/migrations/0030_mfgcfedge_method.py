# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-28 12:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linker', '0029_auto_20171128_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='mfgcfedge',
            name='method',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
