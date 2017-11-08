from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from scipy.stats import hypergeom
# Create your views here.
import json
import numpy as np


from linker.models import *

def index(request):
    return HttpResponse("Hello")


def show_graph(request,analysis_id,metabanalysis_id):
    context_dict = {'analysis_id':analysis_id,'metabanalysis_id':metabanalysis_id}    
    return render(request,'linker/show_graph.html',context_dict)

def get_overlap_strains(request,gcf_id,mf_id):
    gcf = GCF.objects.get(id = gcf_id)
    mf = MF.objects.get(id = mf_id)
    

    gcf_strains = get_gcf_strain_set(gcf)
    mf_strains = get_mf_strain_set(mf)

    overlap = gcf_strains.intersection(mf_strains)
    link = MFGCFEdge.objects.get(gcf = gcf,mf = mf)
    straindict = {'strains': [s.name for s in overlap],'p':link.p}
    return JsonResponse(straindict)

def get_gcf_strain_set(gcf):
    bgcs = [b.bgc for b in gcf.bgcgcf_set.all()]
    strains = set([item.strain for b in bgcs for item in b.bgcstrain_set.all()])
    return strains

def get_gcf_strains(request,gcf_id):
    gcf = GCF.objects.get(id = gcf_id)
    strainlist = [s.name for s in get_gcf_strain_set(gcf)]
    straindict = {'strains':strainlist}
    return JsonResponse(straindict)

def get_mf_strain_set(mf):
    spectra = [s.spectrum for s in mf.spectrummf_set.all()]
    strains = set([item.strain for spectrum in spectra for item in spectrum.spectrumstrain_set.all()])
    return strains

def get_mf_strains(request,mf_id):
    mf = MF.objects.get(id = mf_id)
    strainlist = [s.name for s in get_mf_strain_set(mf)]
    straindict = {'strains':strainlist}
    return JsonResponse(straindict)

def get_graph(request,analysis_id,metabanalysis_id):
    import networkx as nx
    from networkx.readwrite import json_graph

    analysis = Analysis.objects.get(id = analysis_id)
    metabanalysis = MetabAnalysis.objects.get(id = metabanalysis_id)
    G = nx.Graph()
    mfs = MF.objects.filter(metabanalysis = metabanalysis)
    gcfs = GCF.objects.filter(analysis = analysis,gcftype='allPKSI')

    # strains = Strain.objects.all()
    # mfs_list = []
    # for m in mfs:
    #     # n = len(MFStrain.objects.filter(mf = m))
    #     # n = len(get_mf_strain_set(m))
    #     n = 10
    #     mfs_list.append([m.name,{'nstrains': n}])
    #     G.add_node(m.name,nstrains = n,nodetype='mf',dbid = m.id)
    # gcf_list = []
    # for g in gcfs:
    #     # n = len(GCFStrain.objects.filter(gcf = g))
    #     # n = len(get_gcf_strain_set(g))
    #     n = 10
    #     gcf_list.append([g.name,{'nstrains': n,'gcftype': g.gcftype}])
    #     G.add_node(g.name,nstrains = n,gcftype = g.gcftype,nodetype='gcf',dbid = g.id)

    nodes = {}
    p_thresh = 0.01
    links = MFGCFEdge.objects.filter(p__lte = p_thresh,mf__in = mfs,gcf__in = gcfs)
    for link in links:
        if not link.mf.name in nodes:
            n = len(get_mf_strain_set(link.mf))
            # n = 10
            G.add_node(link.mf.name,nstrains = n,nodetype='mf',dbid = link.mf.id)
            nodes[link.mf.name] = True
        if not link.gcf.name in nodes:
            n = len(get_gcf_strain_set(link.gcf))
            # n = 10
            G.add_node(link.gcf.name,nstrains = n,gcftype = link.gcf.gcftype,nodetype='gcf',dbid = link.gcf.id)
            nodes[link.gcf.name] = True
        G.add_edge(link.mf.name,link.gcf.name,weight =-np.log(link.p))
    

    
    return JsonResponse(json_graph.node_link_data(G))