# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-08 14:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('linker', '0009_auto_20171107_0853'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetabAnalysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.CharField(max_length=2048, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='media',
            name='metabanalysis',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='linker.MetabAnalysis'),
        ),
        migrations.AddField(
            model_name='mf',
            name='metabanalysis',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='linker.MetabAnalysis'),
        ),
        migrations.AddField(
            model_name='spectrum',
            name='metabanalysis',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='linker.MetabAnalysis'),
        ),
    ]
