import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import django
django.setup()

from linker.models import *

if __name__ == '__main__':
	analysis_name = sys.argv[1]
	bigscape_outout_dir = sys.argv[2]
	mf_file = sys.argv[3]

	try:
		analysis = Analysis.objects.create(name = analysis_name)
	except:
		print "Analysis already exists"
