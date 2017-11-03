import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

from scipy.stats import hypergeom

import django
django.setup()

from linker.models import *

import json

if __name__ == '__main__':
	mf_file = '/Users/simon/Dropbox/BioResearch/Meta_clustering/MS2LDA/BGC/scripts/other/mol_fam_dict.txt'
	gcf_file = '/Users/simon/Dropbox/BioResearch/Meta_clustering/MS2LDA/BGC/scripts/other/gcf_dict.txt'
	with open(mf_file,'r') as f:
		line = f.readline()

	mf_dict = json.loads(line)


	with open(gcf_file,'r') as f:
		line = f.readline()

	gcf_dict = json.loads(line)
	

	for mfname in mf_dict:
		mf,b = MF.objects.get_or_create(name = mfname)
		for strainname in mf_dict[mfname]:
			strain,b = Strain.objects.get_or_create(name = strainname)
			mfs,b = MFStrain.objects.get_or_create(strain = strain,mf = mf)

	for gcfname in gcf_dict:
		gcftype,strains = gcf_dict[gcfname]
		gcf,b = GCF.objects.get_or_create(name = gcfname)
		gcf.gcftype = gcftype
		gcf.save()
		for strainname in strains:
			strain,b = Strain.objects.get_or_create(name = strainname)
			gfs,b = GCFStrain.objects.get_or_create(strain = strain,gcf = gcf)

	strains = Strain.objects.all()
	mfs = MF.objects.all()
	gcfs = GCF.objects.all()

	print len(strains),len(mfs),len(gcfs)


	mfs = MF.objects.all()
	gcfs = GCF.objects.all()
	strains = Strain.objects.all()


	mol_fam_dict = {}
	for mfstrains in MFStrain.objects.all():
		mf = mfstrains.mf
		strain = mfstrains.strain
		if not mf in mol_fam_dict:
			mol_fam_dict[mf] = [strain]
		else:
			mol_fam_dict[mf].append(strain)

	gcf_dict = {}
	for gcfstrains in GCFStrain.objects.all():
		gcf = gcfstrains.gcf
		strain = gcfstrains.strain
		if not gcf in gcf_dict:
			gcf_dict[gcf] = [strain]
		else:
			gcf_dict[gcf].append(strain)

	p_thresh = 0.05
	n_strains = len(strains)
	for mf in mol_fam_dict:
	    for gcf in gcf_dict:
	        # Compute the overlap
	        mf_strains = set(mol_fam_dict[mf])
	        n_mf_strains = len(mf_strains)
	        gcf_strains = set(gcf_dict[gcf])
	        n_gcf_strains = len(gcf_strains)
	        just_in_mf = mf_strains - gcf_strains
	        just_in_gcf = gcf_strains - mf_strains
	        union = gcf_strains.union(mf_strains)
	        overlap = gcf_strains.intersection(mf_strains)
	        # compute the probability of getting overlap or more if the mf define the urn
	        a = 0
	        for x in range(len(overlap),n_gcf_strains+1):
	            a += hypergeom.pmf(x,n_strains,n_mf_strains,n_gcf_strains)
	        if a<= p_thresh:
	        	e,b = MFGCFEdge.objects.get_or_create(mf = mf,gcf = gcf)
	        	e.p = a
	        	e.save()
	            # edges.append(["MF{}".format(mf.name),"GCF{}".format(gcf.name)])