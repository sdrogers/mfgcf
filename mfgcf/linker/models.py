from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Analysis(models.Model):
	name = models.CharField(unique = True,max_length = 200)
	description = models.CharField(max_length = 2048,null=True)
	def __str__(self):
		return self.name

class Strain(models.Model):
	name = models.CharField(unique=True,max_length=200)
	organism = models.CharField(max_length = 1024,null = True)
	taxonomy = models.CharField(max_length = 2024,null = True)
	def __str__(self):
		return self.name



class BGC(models.Model):
	name = models.CharField(unique=True,max_length=200)
	analysis = models.ForeignKey(Analysis,null=True)
	accession = models.CharField(max_length=200,null=True)
	description= models.CharField(max_length=1024,null=True)
	product = models.CharField(max_length=200,null=True)
	bgsclass = models.CharField(max_length=200,null=True)


class GCF(models.Model):
	name = models.CharField(unique=True,max_length=200)
	gcftype = models.CharField(max_length=200,null=True)
	analysis = models.ForeignKey(Analysis)

class BGCGCF(models.Model):
	bgc = models.ForeignKey(BGC)
	gcf = models.ForeignKey(GCF)

class Spectrum(models.Model):
	suid = models.IntegerField()
	analysis = models.ForeignKey(Analysis,null=True)
	libraryid = models.CharField(max_length = 1024,null = True)
	link = models.CharField(max_length = 1024,null=True)
	def __str__(self):
		return "{},{},{}".format(self.suid,str(self.analysis),self.libraryid)

class MF(models.Model):
	name = models.CharField(unique=True,max_length=200)
	analysis = models.ForeignKey(Analysis)

class BGCStrain(models.Model):
	strain = models.ForeignKey(Strain)
	bgc = models.ForeignKey(BGC)

class SpectrumStrain(models.Model):
	spectrum = models.ForeignKey(Spectrum)
	strain = models.ForeignKey(Strain)
	count = models.IntegerField()

class SpectrumMF(models.Model):
	spectrum = models.ForeignKey(Spectrum)
	mf = models.ForeignKey(MF)

class Media(models.Model):
	name = models.CharField(max_length = 1024)
	analysis = models.ForeignKey(Analysis)

class SpectrumMedia(models.Model):
	spectrum = models.ForeignKey(Spectrum)
	media = models.ForeignKey(Media)
	count = models.IntegerField()

# class MFStrain(models.Model):
# 	strain = models.ForeignKey(Strain)
# 	mf = models.ForeignKey(MF)

class MFGCFEdge(models.Model):
	mf = models.ForeignKey(MF)
	gcf = models.ForeignKey(GCF)
	p = models.FloatField(null = True)