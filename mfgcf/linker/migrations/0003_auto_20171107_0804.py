# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-07 08:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linker', '0002_auto_20171107_0750'),
    ]

    operations = [
        migrations.AddField(
            model_name='strain',
            name='organism',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='strain',
            name='taxonomy',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]