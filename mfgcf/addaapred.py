import argparse
import csv
import glob

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import django
django.setup()

from django.db import transaction
from linker import models

import linker


def find_bgc(analysis, filename):
    """
    Hack to find BGC from filename. Look for matching BGCs in database.
    """
    bgc_fields = filename.split(".")
    match = False
    for i in xrange(len(bgc_fields)):
        name = ".".join(bgc_fields[:i])
        if models.BGC.objects.filter(name=name, analysis=analysis).exists():
            match = models.BGC.objects.get(name=name, analysis=analysis)
            return match


def process_aa_file(analysis, filename):
    basename = os.path.basename(filename)

    bgc = find_bgc(analysis, basename)
    if bgc is None:
        # bgc = models.BGC.objects.create(name=basename)
        pass
    else:
        print 'Processing %s' % basename
        with transaction.atomic():
            with open(filename, 'r') as f:
                reader = csv.reader(f, delimiter=',')
                for aa, prob in reader:
                    bgc_aa, created = models.BGCAASpecificity.objects.get_or_create(bgc=bgc, aa=aa)
                    bgc_aa.prob = float(prob)
                    bgc_aa.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load BGC AA specificity predictions into database")
    parser.add_argument("analysis", help="Analysis name")
    parser.add_argument("inputpath", help="Directory containing csv aa prediction files")
    args = parser.parse_args()

    analysis_name = args.analysis
    inputpath = args.inputpath

    try:
        analysis = models.Analysis.objects.create(name=analysis_name)
    except django.db.utils.IntegrityError:
        print "Analysis already exists"
        analysis = models.Analysis.objects.get(name=analysis_name)

    for f in glob.glob("%s/*_aa.csv" % inputpath):
        process_aa_file(analysis, f)
