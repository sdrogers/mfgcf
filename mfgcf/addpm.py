import os
import sys
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")
import django
django.setup()

from linker.models import *

from django.db import transaction


if __name__ == '__main__':
    """
    Add parent mass & precursor mass (from file -- which file? The Crusemann
    .XLS file?) to the Crusemann data
    """
    metabanalysis = MetabAnalysis.objects.get(name='crusemann')
    filename = sys.argv[1]
    spectra = Spectrum.objects.filter(metabanalysis=metabanalysis)
    spec_dict = {}
    for s in spectra:
        spec_dict[s.rowid] = s

    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=',', dialect='excel')
        heads = reader.next()
        print heads
        # sys.exit(0)
        ppos = heads.index('parent mass')

        prpos = heads.index('precursor mass')
        # spos = heads.index('cluster index')
        spos = heads.index('SUID')
        libpos = heads.index('LibraryID')
        n_done = 0
        with transaction.atomic():
            for line in reader:
                print line, len(line), len(heads)
                print line[ppos], line[prpos], line[spos]
                par = float(line[ppos])
                pre = float(line[prpos])
                spec = spec_dict[int(line[spos])]
                spec.precursormass = pre
                spec.parentmass = par
                spec.save()
                n_done += 1
                if n_done % 1000 == 0:
                    print n_done
