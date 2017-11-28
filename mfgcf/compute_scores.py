import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import argparse
from scipy.stats import hypergeom

import django
django.setup()

from linker.models import *
from django.db import transaction


def compute_scores(analysis, metabanalysis, method, parameters):
    # find all the strains in this analysis
    bgcs = BGC.objects.filter(analysis = analysis)
    b_strains = set([item.strain for b in bgcs for item in b.bgcstrain_set.all()]) # assuming only one strain...
    spectra = Spectrum.objects.filter(metabanalysis = metabanalysis)
    s_strains = []
    s_strains = set([item.strain for s in spectra for item in s.spectrumstrain_set.all()])
    strains = b_strains.union(s_strains)
    print "{} strains".format(len(strains))
    
    # make a mf dictionary of strain sets
    print "Extracting strain sets for MFs"
    mf_dict = {}
    mfs = MF.objects.filter(metabanalysis = metabanalysis)
    # mfs = filter(lambda x: not x.name.startswith('MF_S'),mfs)

    for mf in mfs:
        mf_spectra = [a.spectrum for a in mf.spectrummf_set.all()]
        mf_strains = [item.strain for s in mf_spectra for item in s.spectrumstrain_set.all()]
        mf_dict[mf] = set(mf_strains) 

    # make a gcf dictionary of strain sets
    print "Extracting strain sets for GCFs"
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
    with transaction.atomic():
        for mf in mf_dict:
            for gcf in gcf_dict:
                # Compute the overlap
                mf_strains = mf_dict[mf]
                gcf_strains = gcf_dict[gcf]
                # Do the actual selection of scoring method here,
                # to account for (possibly) different input parameters...
                if method == 'hypergeom':
                    threshold = parameters['threshold']
                    a,result = hg_test(mf_strains, gcf_strains, n_strains, threshold)
                else:
                    raise SystemExit('Unsupported scoring method: %s' % method)
                if result:
                    e, b = MFGCFEdge.objects.get_or_create(mf=mf, gcf=gcf,method = method)
                    e.p = a
                    e.save()
                    # edges.append(["MF{}".format(mf.name),"GCF{}".format(gcf.name)])
            n_mf_done += 1
            if n_mf_done % 100 == 0:
                print "Done {} of {}".format(n_mf_done, len(mf_dict))


def hg_test(mf_strains, gcf_strains, n_strains, p_thresh):
    """
    Hypergeometric test for the number of strains, using mf as ground truth.
    Return True if below threshold, False otherwise.
    """
    n_mf_strains = len(mf_strains)
    n_gcf_strains = len(gcf_strains)
    overlap = gcf_strains.intersection(mf_strains)
    a = 1
    if len(overlap) > 0:
        # compute the probability of getting overlap or more if the mf define the urn
        a = 0
        for x in range(len(overlap), n_gcf_strains+1):
            a += hypergeom.pmf(x, n_strains, n_mf_strains, n_gcf_strains)
        if a <= p_thresh:
            return a,True
    return a,False


def main():
    parser = argparse.ArgumentParser("Rank analysis links")
    parser.add_argument(dest='analysis_name', help='Analysis name')
    parser.add_argument(dest='metabanalysis_name', help='Metabolic analysis name')
    parser.add_argument('-m', dest='method', help='Scoring method (currently only hypergeom) (default: hypergeom (obviously))', default='hypergeom')
    parser.add_argument('-t', dest='threshold', help='Threshold for score (default: 0.05)', default=0.05)
    args = parser.parse_args()

    method = args.method
    threshold = float(args.threshold)
    analysis_name = args.analysis_name
    metabanalysis_name = args.metabanalysis_name

    analysis = Analysis.objects.get(name=analysis_name)
    metabanalysis = MetabAnalysis.objects.get(name=metabanalysis_name)

    # Eventually add p(cryptic), p(noise), etc. for other scoring methods
    parameters = {
            'threshold': threshold,
    }

    compute_scores(analysis, metabanalysis, method, parameters)


if __name__ == '__main__':
    main()
