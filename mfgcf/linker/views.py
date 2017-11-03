from django.shortcuts import render
from django.http import HttpResponse
from scipy.stats import hypergeom
# Create your views here.
import json
import numpy as np


from linker.models import *

def index(request):
	return HttpResponse("Hello")

def example_graph(request):
	mfs = MF.objects.all()
	gcfs = GCF.objects.all()

	strains = Strain.objects.all()
	mfs_list = []
	for m in mfs:
		n = len(MFStrain.objects.filter(mf = m))
		mfs_list.append(["MF{}".format(m.name),{'nstrains': n}])
	gcf_list = []
	for g in gcfs:
		n = len(GCFStrain.objects.filter(gcf = g))
		gcf_list.append(["GCF{}".format(g.name),{'nstrains': n,'gcftype': g.gcftype}])

	# context_dict = {'mfs':json.dumps(['MF{}'.format(m.name) for m in mfs])}
	context_dict = {}
	context_dict['mfs'] = json.dumps(mfs_list)
	context_dict['strains'] = json.dumps([s.name for s in strains])
	context_dict['gcfs'] = json.dumps(gcf_list)
	edges = []

	p_thresh = 0.01
	links = MFGCFEdge.objects.filter(p__lte = p_thresh)
	for link in links:
	    edges.append(["MF{}".format(link.mf.name),"GCF{}".format(link.gcf.name),-np.log(link.p)])
	        
	# edges.append([mfstrains.strain.name,mfstrains.mf.name])
	context_dict['edges'] = json.dumps(edges)

	



	return render(request,'linker/example_graph.html',context_dict)