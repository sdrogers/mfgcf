# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-07 08:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('linker', '0006_auto_20171107_0846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spectrum',
            name='analysis',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='linker.Analysis'),
        ),
    ]