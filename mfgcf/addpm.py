import os,sys,csv
os.environ.setdefault("DJANGO_SETTINGS_MODULE","mfgcf.settings")
import django
django.setup()

from linker.models import *


if __name__ == '__main__':
  metabanalysis = MetabAnalysis.objects.get(name = 'duncanM')
  filename = sys.argv[1]
  spectra = Spectrum.objects.filter(metabanalysis = metabanalysis)
  spec_dict = {}
  for s in spectra:
      spec_dict[s.rowid] = s

  with open(filename,'r') as f:
    reader = csv.reader(f,delimiter = '\t',dialect = 'excel')
    heads = reader.next()
    print heads[:10]
    ppos = heads.index('parent mass')
    spos = heads.index('cluster index')
    libpos = heads.index('LibraryID')
    for line in reader:
        pm = float(line[ppos])
        spec = spec_dict[int(line[spos])]
        spec.parentmass = pm
        spec.save()

