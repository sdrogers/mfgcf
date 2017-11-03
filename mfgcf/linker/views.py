from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from scipy.stats import hypergeom
# Create your views here.
import json
import numpy as np


from linker.models import *

def index(request):
    return HttpResponse("Hello")


def show_graph(request):    
    return render(request,'linker/show_graph.html',{})

def get_overlap_strains(request,gcf_id,mf_id):
    gcf = GCF.objects.get(id = gcf_id)
    mf = MF.objects.get(id = mf_id)
    gcf_strains = set([g.strain for g in gcf.gcfstrain_set.all()])
    mf_strains = set([g.strain for g in mf.mfstrain_set.all()])
    overlap = gcf_strains.intersection(mf_strains)
    link = MFGCFEdge.objects.get(gcf = gcf,mf = mf)
    straindict = {'strains': [s.name for s in overlap],'p':link.p}
    return JsonResponse(straindict)

def get_gcf_strains(request,gcf_id):
    gcf = GCF.objects.get(id = gcf_id)
    strains = [g.strain for g in gcf.gcfstrain_set.all()]
    strainlist = [s.name for s in strains]
    straindict = {'strains':strainlist}
    return JsonResponse(straindict)

def get_mf_strains(request,mf_id):
    mf = MF.objects.get(id = mf_id)
    strains = [g.strain for g in mf.mfstrain_set.all()]
    strainlist = [s.name for s in strains]
    straindict = {'strains':strainlist}
    return JsonResponse(straindict)

def get_graph(request):
    import networkx as nx
    from networkx.readwrite import json_graph

    G = nx.Graph()
    mfs = MF.objects.all()
    gcfs = GCF.objects.all()

    strains = Strain.objects.all()
    mfs_list = []
    for m in mfs:
        n = len(MFStrain.objects.filter(mf = m))
        mfs_list.append(["MF{}".format(m.name),{'nstrains': n}])
        G.add_node("MF{}".format(m.name),nstrains = n,nodetype='mf',dbid = m.id)
    gcf_list = []
    for g in gcfs:
        n = len(GCFStrain.objects.filter(gcf = g))
        gcf_list.append(["GCF{}".format(g.name),{'nstrains': n,'gcftype': g.gcftype}])
        G.add_node("GCF{}".format(g.name),nstrains = n,gcftype = g.gcftype,nodetype='gcf',dbid = g.id)


    p_thresh = 0.01
    links = MFGCFEdge.objects.filter(p__lte = p_thresh)
    for link in links:
        G.add_edge("MF{}".format(link.mf.name),"GCF{}".format(link.gcf.name),weight =-np.log(link.p))
            
    return JsonResponse(json_graph.node_link_data(G))