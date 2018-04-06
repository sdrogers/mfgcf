import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import argparse
from scipy.stats import hypergeom
import scipy

import django
django.setup()

from linker.models import *
from django.db import transaction


def compute_scores(analysis, metabanalysis, method, parameters):
    # find all the strains in this analysis
    bgcs = BGC.objects.filter(analysis=analysis)
    b_strains = set([item.strain for b in bgcs for item in b.bgcstrain_set.all()])  # assuming only one strain...
    spectra = Spectrum.objects.filter(metabanalysis=metabanalysis)
    s_strains = []
    s_strains = set([item.strain for s in spectra for item in s.spectrumstrain_set.all()])
    strains = b_strains.union(s_strains)
    print "{} strains".format(len(strains))

    # make a mf dictionary of strain sets
    print "Extracting strain sets for MFs"
    mf_dict = {}
    mfs = MF.objects.filter(metabanalysis=metabanalysis)
    # mfs = filter(lambda x: not x.name.startswith('MF_S'),mfs)

    for mf in mfs:
        mf_spectra = [a.spectrum for a in mf.spectrummf_set.all()]
        mf_strains = [item.strain for s in mf_spectra for item in s.spectrumstrain_set.all()]
        mf_dict[mf] = set(mf_strains)

    # make a gcf dictionary of strain sets
    print "Extracting strain sets for GCFs"
    gcf_dict = {}
    gcfs = GCF.objects.filter(analysis=analysis)
    for gcf in gcfs:
        gcf_bgc = [a.bgc for a in gcf.bgcgcf_set.all()]
        gcf_strains = [item.strain for b in gcf_bgc for item in b.bgcstrain_set.all()]
        gcf_dict[gcf] = set(gcf_strains)

    # Computing hypergeometric stats
    print "Computing overlap stats (scoring method: %s)" % method
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
                    value, result = hg_test(mf_strains, gcf_strains, n_strains, threshold)
                elif method == 'correlation':
                    threshold = parameters['threshold']
                    value, result = correlation_test(mf_strains, gcf_strains, n_strains, threshold)
                elif method == 'generative':
                    value, result = generative_test(mf_strains, gcf_strains, n_strains, parameters)
                elif method == 'hg_aa':
                    threshold = parameters['threshold']
                    hg_value, result = hg_test(mf_strains, gcf_strains, n_strains, threshold)
                    # Do we do this by molecular family, instead of spectrum by spectrum?
                    # Consensus?
                    aa_value = aa_test(mf, gcf)
                    value = (1 - aa_value) * hg_value
                else:
                    raise SystemExit('Unsupported scoring method: %s' % method)
                # Success/failure is determined by the comparison algorithm itself?
                # Is that a good idea?
                if result:
                    e, b = MFGCFEdge.objects.get_or_create(mf=mf, gcf=gcf, method=method)
                    e.p = value
                    e.save()
                    # edges.append(["MF{}".format(mf.name),"GCF{}".format(gcf.name)])
            n_mf_done += 1
            if n_mf_done % 100 == 0:
                print "Done {} of {}".format(n_mf_done, len(mf_dict))


def aa_test(mf, gcf):
    # Required consensus prediction across the GCF for a prediction to be
    # considered reliable
    consensus_threshold = 0.75
    # Bin size for AA detection
    aa_sensitivity = 0.05

    # If we are doing this by molecular family, AA prescence is decided by consensus

    gcf_aa_probabilities = {}
    # Get the constituent BGCs of the GCF
    bgcs = BGC.objects.filter(bgcgcf__gcf=gcf)
    # Get the specific edges that link the BGC to the GCF and extract the probabilities
    edges = [x.bgcgcf_set.filter(gcf=gcf) for x in bgcs]
    edge_probabilities = [[z.prob for z in x] for x in edges]

    # add the weighted probabilities
    bgc_prob_sum = 0
    for bgc, bgc_prob in zip(bgcs, edge_probabilities):
        if len(bgc_prob) != 1:
            print 'invalid bgc prob length!'
        bgc_prob = bgc_prob[0]
        for aa_prob_entry in BGCAASpecificity.objects.filter(bgc=bgc):
            aa = aa_prob_entry.aa
            aa_prob = aa_prob_entry.prob
            if aa in gcf_aa_probabilities:
                gcf_aa_probabilities[aa] += bgc_prob * aa_prob
            else:
                gcf_aa_probabilities[aa] = bgc_prob * aa_prob
        bgc_prob_sum += bgc_prob

    for key in gcf_aa_probabilities.keys():
        gcf_aa_probabilities[key] /= bgc_prob_sum

    # Get the measured AA shifts.
    aa_shifts = Shift.objects.filter(source='aa')
    aa_shift_dict = dict([(x.name, x.shift) for x in aa_shifts])

    # - get spectra for mf
    # - get AAs in each spectrum
    consensus_shifts = None
    for spectrum in Spectrum.objects.filter(spectrummf__mf=mf):
        peaks = Peak.objects.filter(spectrum=spectrum)
        peak_locations = [p.position for p in peaks]

        aa_in_peaks = find_shifts(peak_locations, aa_shift_dict, threshold=aa_sensitivity)
        if consensus_shifts is None:
            consensus_shifts = set(aa_in_peaks)
        else:
            consensus_shifts = consensus_shifts.intersection(aa_in_peaks)

    if len(consensus_shifts) == 0:
        score = 0.0
    else:
        score = 1.0
        for aa, prob in gcf_aa_probabilities.items():
            if prob > consensus_threshold:
                if aa in consensus_shifts:
                    score *= prob
                else:
                    score *= (1 - prob)
        # Smooth the scoring to reflect the fact that even for a confidence
        # score of 1.0 we don't want to completely flatten the probabilities.
        # Scale to [0.05, 0.95]
        score = score * 0.9 + 0.05

    return score


def find_shifts(locations, shift_dict, threshold=0.05):
    shifts_in_spectrum = []
    for i in xrange(len(locations)):
        for j in xrange(i):
            delta = locations[i] - locations[j]
            for label, shift in shift_dict.items():
                if abs(delta - shift) < threshold:
                    shifts_in_spectrum.append(label)

    return shifts_in_spectrum


def generative_test(mf_strains, gcf_strains, n_strains, parameters):
    """
    generative model for MF / GCF probability.
    Given the presence / absence of strain in GCF, how likely is the particular
    presence / absence of strains in the MS data?
    Parameters are probability of the BGC being cryptic, and the MS FP rate
    (i.e. probability of MS signal in the abscence of BGC)
    """
    threshold = parameters['threshold']
    p_cryptic = parameters['p_cryptic']
    p_noise = parameters['p_noise']

    mf_strains = set(mf_strains)
    gcf_strains = set(gcf_strains)
    intersection_count = len(mf_strains.intersection(gcf_strains))
    cryptic_count = len(gcf_strains - mf_strains)
    fp_count = len(mf_strains - gcf_strains)
    tn_count = n_strains - (intersection_count + cryptic_count + fp_count)

    value = (1 - p_cryptic) ** intersection_count \
        * p_cryptic ** cryptic_count \
        * p_noise ** fp_count \
        * (1 - p_noise) ** tn_count

    if value > threshold:
        return value, True
    else:
        return value, False


def correlation_test(list_1, list_2, n_strains, p_thresh):
    """
    Pearson's correlation test. Returns True if p value is below threshold.
    """
    all_ids = set.union(set(list_1), set(list_2))
    vector_1 = [1 if i in list_1 else 0 for i in all_ids]
    vector_2 = [1 if i in list_2 else 0 for i in all_ids]

    if len(set(vector_1)) == 1 or len(set(vector_2)) == 1:
        return 1.0, False

    tail = [0] * (n_strains - len(all_ids))
    vector_1.extend(tail)
    vector_2.extend(tail)

    correlation, p_value = scipy.stats.pearsonr(vector_1, vector_2)

    if p_value < p_thresh:
        return p_value, True
    else:
        return p_value, False


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
            return a, True
    return a, False


def main():
    parser = argparse.ArgumentParser("Rank analysis links")
    parser.add_argument(dest='analysis_name', help='Analysis name')
    parser.add_argument(dest='metabanalysis_name', help='Metabolic analysis name')
    parser.add_argument('-m', dest='method', help='Scoring method (currently only hypergeom) (default: hypergeom (obviously))', default='hypergeom')
    parser.add_argument('-t', dest='threshold', help='Threshold for score (default: 0.05)', default=0.05)
    parser.add_argument('--p_cryptic', dest='p_cryptic', help='Probability of a cluster being cryptic (generative only, default: 0.33)', default=0.33)
    parser.add_argument('--p_noise', dest='p_noise', help='Probability of FP in MS, given BGC data (includes BGC FN rate) (generative only, default 0.01)', default=0.01)
    args = parser.parse_args()

    method = args.method
    threshold = float(args.threshold)
    analysis_name = args.analysis_name
    metabanalysis_name = args.metabanalysis_name

    analysis = Analysis.objects.get(name=analysis_name)
    metabanalysis = MetabAnalysis.objects.get(name=metabanalysis_name)

    # Eventually add p(cryptic), p(noise), etc. for other scoring methods
    parameters = {
            'threshold': float(threshold),
            'p_cryptic': float(args.p_cryptic),
            'p_noise': float(args.p_noise)
    }

    compute_scores(analysis, metabanalysis, method, parameters)


if __name__ == '__main__':
    main()
