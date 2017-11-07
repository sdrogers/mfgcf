from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Analysis(models.Model):
	name = models.CharField(unique = True,max_length = 200)
	description = models.CharField(max_length = 2048,null=True)

class Strain(models.Model):
	name = models.CharField(unique=True,max_length=200)

class BGC(models.Model):
	name = models.CharField(unique=True,max_length=200)
	analysis = models.ForeignKey(Analysis,null=True)

class GCF(models.Model):
	name = models.CharField(unique=True,max_length=200)
	gcftype = models.CharField(max_length=200,null=True)
	analysis = models.ForeignKey(Analysis)

class MF(models.Model):
	name = models.CharField(unique=True,max_length=200)
	analysis = models.ForeignKey(Analysis)

class BGCStrain(models.Model):
	strain = models.ForeignKey(Strain)
	bgc = models.ForeignKey(BGC)

class MFStrain(models.Model):
	strain = models.ForeignKey(Strain)
	mf = models.ForeignKey(MF)

class MFGCFEdge(models.Model):
	mf = models.ForeignKey(MF)
	gcf = models.ForeignKey(GCF)
	p = models.FloatField(null = True)