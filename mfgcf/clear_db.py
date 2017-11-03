import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import django
django.setup()

from linker.models import *

if __name__ == '__main__':
	# clear the db
	strains = Strain.objects.all()
	for s in strains:
		s.delete()

	mfs = MF.objects.all()
	for m in mfs:
		m.delete()

	gcfs = GCF.objects.all()
	for g in gcfs:
		g.delete()

	links = MFGCFEdge.objects.all()
	for l in links:
		l.delete()