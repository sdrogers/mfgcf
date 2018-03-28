# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-28 14:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('linker', '0033_mychunkedupload'),
    ]

    operations = [
        migrations.CreateModel(
            name='BGCAASpecificity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aa', models.CharField(max_length=3)),
                ('prob', models.FloatField(null=True)),
                ('bgc', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='linker.BGC')),
            ],
        ),
    ]
