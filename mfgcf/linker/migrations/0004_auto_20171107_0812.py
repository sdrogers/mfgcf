# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-07 08:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linker', '0003_auto_20171107_0804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strain',
            name='taxonomy',
            field=models.CharField(max_length=2024, null=True),
        ),
    ]
