# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-28 13:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('linker', '0030_mfgcfedge_method'),
    ]

    operations = [
        migrations.CreateModel(
            name='BGCtoMiBIG',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('bgc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='linker.BGC')),
                ('mibig', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='linker.MiBIG')),
            ],
        ),
    ]
