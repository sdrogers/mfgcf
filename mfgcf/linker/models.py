from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Strain(models.Model):
	name = models.CharField(unique=True,max_length=200)

class GCF(models.Model):
	name = models.CharField(unique=True,max_length=200)

class MF(models.Model):
	name = models.CharField(unique=True,max_length=200)

class GCFStrain(models.Model):
	strain = models.ForeignKey(Strain)
	gcf = models.ForeignKey(GCF)

class MFStrain(models.Model):
	strain = models.ForeignKey(Strain)
	mf = models.ForeignKey(MF)