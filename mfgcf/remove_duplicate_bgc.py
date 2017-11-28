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
		bgcs = BGC.objects.filter(analysis = analysis)
		print "Found {} bgcs".format(len(bgcs))
		matches = {}
		for bgc in bgcs:
			if not bgc.name in matches:
				matches[bgc.name] = [bgc]
			else:
				matches[bgc.name].append(bgc)
		print "Found {} unique BGC".format(len(matches))



if __name__ == '__main__':
	main()
