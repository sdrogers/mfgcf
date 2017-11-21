import os,sys,csv
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import django
django.setup()

from django.db import transaction

mibig_file = 'mibig.tsv'

from linker.models import *

if __name__ == '__main__':
	MiBIG.objects.all().delete()
	with transaction.atomic():
		with open(mibig_file,'r') as f:
			n_loaded = 0
			reader = csv.reader(f,delimiter = '\t',dialect = 'excel')
			for line in reader:
				name = line[0]
				product = line[2]
				bgcclass = line[3]
				organism = line[4]
				mibig,_ = MiBIG.objects.get_or_create(name = name)
				mibig.product = product
				mibig.bgcclass = bgcclass
				mibig.organism = organism
				url = "https://mibig.secondarymetabolites.org/repository/{}/index.html#cluster-1".format(name)
				mibig.url = url
				mibig.save()
				bgcs = BGC.objects.filter(name__startswith = name)
				for b in bgcs:
					b.mibig = mibig
					b.save()
				n_loaded += 1
				if n_loaded % 100 == 0:
					print n_loaded
