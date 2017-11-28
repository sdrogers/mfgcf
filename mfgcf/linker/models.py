from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Analysis(models.Model):
    name = models.CharField(unique = True,max_length = 200)
    description = models.CharField(max_length = 2048,null=True)
    def __str__(self):
        return self.name

class MetabAnalysis(models.Model):
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

class GCFClass(models.Model):
    name = models.CharField(max_length = 100,null = False)
    source = models.CharField(max_length = 100,null = False)
    def __str__(self):
        return "{} ({})".format(self.name,self.source)

class MiBIG(models.Model):
    name = models.CharField(max_length = 100,unique = True)
    product = models.CharField(max_length = 1024)
    bgcclass = models.CharField(max_length=200,null=True)
    url = models.CharField(max_length=1024,null=True)
    organism = models.CharField(max_length=200,null=True)
    def __str__(self):
        return "{}: {}".format(self.name,self.product)


class BGC(models.Model):
    name = models.CharField(max_length=200)
    analysis = models.ForeignKey(Analysis,null=True)
    accession = models.CharField(max_length=200,null=True)
    description = models.CharField(max_length=1024,null=True)
    product = models.CharField(max_length=200,null=True)
    bgcclass = models.CharField(max_length=200,null=True)
    mibig = models.ForeignKey(MiBIG,null=True)


class GCF(models.Model):
    name = models.CharField(max_length=200)
    analysis = models.ForeignKey(Analysis)
    @property
    def gcftype(self):
        classlinks = self.gcftoclass_set.all()
        classnames = [c.gcfclass.name for c in classlinks]
        return ",".join(classnames)

    @property
    def gcftypeset(self):
        classlinks = self.gcftoclass_set.all()
        return set([c.gcfclass for c in classlinks])


    @property
    def mibig(self):
        bgc = [b.bgc for b in self.bgcgcf_set.all()]
        mibig = None
        for b in bgc:
            if b.mibig:
                if not mibig:
                    mibig = []
                mibig.append(b.mibig)
        return mibig

    @property
    def degree(self):
        return len(self.bgcgcf_set.all())


class GCFtoClass(models.Model):
    gcf = models.ForeignKey(GCF)
    gcfclass = models.ForeignKey(GCFClass)
    original_name = models.CharField(max_length = 100,null = True)

class BGCGCF(models.Model):
    bgc = models.ForeignKey(BGC)
    gcf = models.ForeignKey(GCF)

class Spectrum(models.Model):
    rowid = models.IntegerField()
    metabanalysis = models.ForeignKey(MetabAnalysis,null=True)
    libraryid = models.CharField(max_length = 1024,null = True)
    link = models.CharField(max_length = 1024,null=True)
    parentmass = models.FloatField(null=True)
    precursormass = models.FloatField(null=True)
    def __str__(self):
        return "{},{},{}".format(self.rowid,str(self.metabanalysis),self.libraryid)

class MF(models.Model):
    name = models.CharField(max_length=200)
    metabanalysis = models.ForeignKey(MetabAnalysis,null=True)

    @property
    def libid(self):
        spec = [s.spectrum for s in self.spectrummf_set.all()]
        libid = None
        for s in spec:
            if not s.libraryid == 'N/A':
                if not libid:
                    libid = []
                libid.append(s.libraryid)
        return libid

class BGCStrain(models.Model):
    strain = models.ForeignKey(Strain)
    bgc = models.ForeignKey(BGC)

class SpectrumStrain(models.Model):
    spectrum = models.ForeignKey(Spectrum)
    strain = models.ForeignKey(Strain)
    count = models.IntegerField()
    parentmass = models.FloatField(null = True)

class SpectrumMF(models.Model):
    spectrum = models.ForeignKey(Spectrum)
    mf = models.ForeignKey(MF)

class Media(models.Model):
    name = models.CharField(max_length = 1024)
    metabanalysis = models.ForeignKey(MetabAnalysis,null=True)

class SpectrumMedia(models.Model):
    spectrum = models.ForeignKey(Spectrum)
    media = models.ForeignKey(Media)
    count = models.IntegerField()

# class MFStrain(models.Model):
#   strain = models.ForeignKey(Strain)
#   mf = models.ForeignKey(MF)

class MFGCFEdge(models.Model):
    mf = models.ForeignKey(MF)
    gcf = models.ForeignKey(GCF)
    p = models.FloatField(null = True)
    validated = models.BooleanField(default = False)
    def __str__(self):
        return "{}->{}".format(self.mf.name,self.gcf.name)
