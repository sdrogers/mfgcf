import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

from scipy.stats import hypergeom

import django
django.setup()

from linker.models import *


def compute_h_scores(analysis):
    p_thresh = 0.01

    # find all the strains in this analysis
    bgcs = BGC.objects.filter(analysis = analysis)
    b_strains = set([item.strain for b in bgcs for item in b.bgcstrain_set.all()]) # assuming only one strain...
    spectra = Spectrum.objects.filter(analysis = analysis)
    s_strains = []
    s_strains = set([item.strain for s in spectra for item in s.spectrumstrain_set.all()])
    strains = b_strains.union(s_strains)
    print "{} strains".format(len(strains))
    
    # make a mf dictionary of strain sets
    print "Extracting strain sets for MFs"
    mf_dict = {}
    mfs = MF.objects.filter(analysis = analysis)
    for mf in mfs:
        mf_spectra = [a.spectrum for a in mf.spectrummf_set.all()]
        mf_strains = [item.strain for s in mf_spectra for item in s.spectrumstrain_set.all()]
        mf_dict[mf] = set(mf_strains) 

    # make a gcf dictionary of strain sets
    print "Extractig strain sets for GCFs"
    gcf_dict = {}
    gcfs = GCF.objects.filter(analysis = analysis)
    for gcf in gcfs:
        gcf_bgc = [a.bgc for a in gcf.bgcgcf_set.all()]
        gcf_strains = [item.strain for b in gcf_bgc for item in b.bgcstrain_set.all()]
        gcf_dict[gcf] = set(gcf_strains)

    # Computing hypergeometric stats
    print "Computing hg stats"
    n_strains = len(strains)
    n_mf_done = 0
    for mf in mf_dict:
        for gcf in gcf_dict:
            # Compute the overlap
            mf_strains = mf_dict[mf]
            n_mf_strains = len(mf_strains)
            gcf_strains = gcf_dict[gcf]
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
        n_mf_done += 1
        if n_mf_done % 1 == 0:
            print "Done {} of {}".format(n_mf_done,len(mf_dict))

if __name__ == '__main__':
    analysis_name = sys.argv[1]
    analysis = Analysis.objects.get(name = analysis_name)
    compute_h_scores(analysis)
    
