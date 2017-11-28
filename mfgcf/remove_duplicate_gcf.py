import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import django
django.setup()


from linker.models import *
from django.db import transaction

def main():
	analyses = Analysis.objects.all()
	for analysis in analyses:
		with transaction.atomic():
			print analysis
			gcfs = GCF.objects.filter(analysis = analysis)
			print "Found {} GCFs".format(len(gcfs))
			unique = {}
			for gcf in gcfs:
				bgcs = sorted([str(b.bgc.id) for b in gcf.bgcgcf_set.all()])
				bs = ":".join(bgcs)
				if bs in unique:
					unique[bs].append(gcf)
				else:
					unique[bs] = [gcf]
			print "Found {} unique GCF".format(len(unique))

			# the first one remains, just add a gcftoclass object
			# subsequent ones, add a new gcftoclass object from the original one
			# redirect all edge objects to the original one
			todelete = []
			for gcfstring,gcfs in unique.items():
				if len(gcfs) > 1:
					orig = gcfs[0]
					gcfclass = GCFClass.objects.get(name = orig.gcftype,source = 'BIGSCAPE')
					GCFtoClass.objects.get_or_create(gcf = orig,gcfclass = gcfclass)
					for other in gcfs[1:]:
						gcfclass = GCFClass.objects.get(name = other.gcftype,source = 'BIGSCAPE')
						GCFtoClass.objects.get_or_create(gcf = orig,gcfclass = gcfclass)
						# because edges are computed on strains via BGCs, if the BGCs are the same 
						# which they have to be to get here, we dont need to add any edges
						todelete.append(other)
			for o in todelete:
				o.delete()



if __name__ == '__main__':
	main()