import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import django
django.setup()


from linker.models import *

def main():
	analyses = Analysis.objects.all()
	for analysis in analyses:
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
		break	


if __name__ == '__main__':
	main()