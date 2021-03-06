# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-28 09:01
from __future__ import unicode_literals

from django.db import migrations

GCF_TYPES = ['allRiPPs','allPKSother','allOthers','allNRPS','allPKSI','allPKS-NRP','allSaccharides','allTerpene']
source = 'BIGSCAPE'

from linker.models import GCFClass

def add_bigscape_classes(apps,schema_editor):
	for t in GCF_TYPES:
		GCFClass.objects.get_or_create(name = t,source = source)

class Migration(migrations.Migration):

    dependencies = [
        ('linker', '0022_gcfclass'),
    ]

    operations = [
    	migrations.RunPython(add_bigscape_classes)
    ]
