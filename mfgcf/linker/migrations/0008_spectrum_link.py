# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-07 08:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linker', '0007_auto_20171107_0847'),
    ]

    operations = [
        migrations.AddField(
            model_name='spectrum',
            name='link',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]
