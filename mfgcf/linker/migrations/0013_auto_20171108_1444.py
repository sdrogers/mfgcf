# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-08 14:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linker', '0012_auto_20171108_1443'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='analysis',
        ),
        migrations.RemoveField(
            model_name='mf',
            name='analysis',
        ),
        migrations.RemoveField(
            model_name='spectrum',
            name='analysis',
        ),
    ]
