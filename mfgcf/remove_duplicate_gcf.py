import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import django
django.setup()


from linker.models import *
from django.db import transaction

GCF_TYPES = ['allRiPPs','allPKSother','allOthers','allNRPS','allPKSI','allPKS-NRP','allSaccharides','allTerpene']


def main():
	analyses = Analysis.objects.all()
	for analysis in analyses:
		gcf_no = 0
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
					gcftype = orig.name.split('_')[1]
					gcfclass = GCFClass.objects.get(name = gcftype,source = 'BIGSCAPE')
					GCFtoClass.objects.get_or_create(gcf = orig,gcfclass = gcfclass,original_name = orig.name)
					for other in gcfs[1:]:
						gcftype = other.name.split('_')[1]
						gcfclass = GCFClass.objects.get(name = gcftype,source = 'BIGSCAPE')
						GCFtoClass.objects.get_or_create(gcf = orig,gcfclass = gcfclass,original_name = other.name)
						# because edges are computed on strains via BGCs, if the BGCs are the same 
						# which they have to be to get here, we dont need to add any edges
						todelete.append(other)
					tokens = orig.name.split('_')
					if tokens[1] in GCF_TYPES:
						newname = "GCF_{}_{}".format(analysis.name,gcf_no)
						gcf_no += 1
						orig.name = newname
						orig.save()
				else:
					orig = gcfs[0]
					gcftype = orig.name.split('_')[1]
					gcfclass = GCFClass.objects.get(name = gcftype,source = 'BIGSCAPE')
					GCFtoClass.objects.get_or_create(gcf = orig,gcfclass = gcfclass,original_name = orig.name)
					tokens = orig.name.split('_')
					if tokens[1] in GCF_TYPES:
						newname = "GCF_{}_{}".format(analysis.name,gcf_no)
						gcf_no += 1
						orig.name = newname
						orig.save()



			for o in todelete:
				o.delete()

def fixnames():
	gcfs = GCF.objects.all()
	with transaction.atomic():
		for g in gcfs:
			g.gcftype = g.name.split('_')[1]
			g.save()

def fixnames2():
	analyses = Analysis.objects.all()
	for analysis in analyses:
		with transaction.atomic():
			gcf = GCF.objects.filter(analysis = analysis)
			# find the max gcf_no
			max_no = 0
			to_fix = []
			for g in gcf:
				tokens = g.name.split('_')
				if not tokens[1] in GCF_TYPES:
					if int(tokens[-1]) > max_no:
						max_no = int(tokens[-1])
				else:
					to_fix.append(g)
			gcf_no = max_no + 1
			for g in to_fix:
				tokens = g.name.split('_')
				newname = "GCF_{}_{}".format(analysis.name,gcf_no)
				gcf_no += 1
				try:
					gcfclass = GCFClass.objects.get(name = tokens[1])
				except:
					print tokens[1]
					break
				GCFtoClass.objects.get_or_create(gcf = g,gcfclass = gcfclass,original_name = g.name)
				g.name = newname
				g.save()


if __name__ == '__main__':
	# fixnames() Needed once when simon screwed up the db
	# fixnames2() Ditto
	main()
	