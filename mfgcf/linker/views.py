from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.db import transaction
from scipy.stats import hypergeom
# Create your views here.
import json
import numpy as np



GCF_TYPES = ['allRiPPs','allPKSother','allOthers','allNRPS','allPKSI','allPKS-NRP','allSaccharides','allTerpene']


from linker.models import *
from linker.forms import *

def index(request):
    analyses = Analysis.objects.all()
    context_dict = {'analyses': analyses}
    metabanalyses = MetabAnalysis.objects.all()
    context_dict['metabanalyses'] = metabanalyses
    return render(request,'linker/index.html',context_dict)

def show_validated(request):
    context_dict = {}
    vlinks = MFGCFEdge.objects.filter(validated = True)
    context_dict['vlinks'] = vlinks
    return render(request,'linker/vlinks.html',context_dict)

def show_analysis(request,analysis_id):
    analysis = Analysis.objects.get(id = analysis_id)
    context_dict = {}
    context_dict['analysis'] = analysis
    metabanalyses = MetabAnalysis.objects.all()
    context_dict['metabanalyses'] = metabanalyses
    gcfs = GCF.objects.filter(analysis = analysis)
    context_dict['gcfs'] = gcfs
    return render(request,'linker/analysis.html',context_dict)

def show_spectra(request,metabanalysis_id):
    metabanalysis = MetabAnalysis.objects.get(id = metabanalysis_id)
    spectra = Spectrum.objects.filter(metabanalysis = metabanalysis)
    mfs = []
    for s in spectra:
        mfs.append(s.spectrummf_set.all()[0].mf)
    spectra = zip(spectra,mfs)
    context_dict = {}
    context_dict['metabanalysis'] = metabanalysis
    context_dict['spectra'] = spectra
    return render(request,'linker/spectra.html',context_dict)

def show_metabanalysis(request,metabanalysis_id):
    metabanalysis = MetabAnalysis.objects.get(id = metabanalysis_id)
    analyses = Analysis.objects.all()
    context_dict = {}
    context_dict['metabanalysis'] = metabanalysis
    context_dict['analyses'] = analyses

    return render(request,'linker/metabanalysis.html',context_dict)

def show_allmf(request,metabanalysis_id):
    context_dict = {}
    metabanalysis = MetabAnalysis.objects.get(id = metabanalysis_id)
    context_dict['metabanalysis'] = metabanalysis
    context_dict['mfs'] = MF.objects.filter(metabanalysis = metabanalysis).order_by('name')
    return render(request,'linker/allmf.html',context_dict)


def validate_from_mf(request,link_id):
    link = MFGCFEdge.objects.get(id = link_id)
    if link.validated:
        link.validated = False
    else:
        link.validated = True
    link.save()
    return HttpResponseRedirect("/linker/showmf/{}".format(link.mf.id))

def validate_from_gcf(request,link_id):
    link = MFGCFEdge.objects.get(id = link_id)
    if link.validated:
        link.validated = False
    else:
        link.validated = True
    link.save()
    print request.path_info
    print request.META.get('HTTP_')
    return HttpResponseRedirect("/linker/showgcf/{}".format(link.gcf.id))


def show_links(request, analysis_id, metabanalysis_id):

    context_dict = {'analysis_id': analysis_id, 'metabanalysis_id': metabanalysis_id}
    analysis = Analysis.objects.get(id=analysis_id)
    metabanalysis = MetabAnalysis.objects.get(id=metabanalysis_id)
    context_dict['analysis'] = analysis
    context_dict['metabanalysis'] = metabanalysis

    if request.method == 'POST':
        # form has been submitted

        # compute the integer value encoding which families to show
        form = GraphForm(request.POST)
        if form.is_valid():

            gcftypes = form.cleaned_data['families']
            gcfclasses = []
            for g in gcftypes:
                gcfclasses.append(GCFClass.objects.get(name=g, source='BIGSCAPE'))

            families = 0
            for i,g in enumerate(GCF_TYPES):
                po = len(GCF_TYPES) - 1 - i
                if g in gcftypes:
                    families += 2**po
            print gcftypes,families
            context_dict['families'] = families
            context_dict['link_threshold'] = form.cleaned_data['link_threshold']

            mfs = MF.objects.filter(metabanalysis=metabanalysis)
            gcfs = GCF.objects.filter(analysis=analysis, gcftoclass__gcfclass__in=gcfclasses)
            p_thresh = form.cleaned_data['link_threshold']
            links = MFGCFEdge.objects.filter(mf__in=mfs, gcf__in=gcfs, p__lte=p_thresh)
            links2 = MFGCFEdge.objects.filter(validated=True, mf__in=mfs, gcf__in=gcfs)
            links = list(set(list(links) + list(links2)))
            print "{},{},found {} links".format(analysis, metabanalysis, len(links))

            strain_sets = {}
            link_list = []
            for link in links:
                sub_list = []
                sub_list.append(link.mf)
                sub_list.append(link.gcf)
                sub_list.append(link.p)
                if not link.mf in strain_sets:
                    strain_sets[link.mf] = get_mf_strain_set(link.mf)
                if not link.gcf in strain_sets:
                    strain_sets[link.gcf] = get_gcf_strain_set(link.gcf)

                sub_list.append(strain_sets[link.mf].union(strain_sets[link.gcf]))
                link_list.append(sub_list)

            link_list = sorted(link_list, key=lambda x: x[2])
            context_dict['link_list'] = link_list
            return render(request, 'linker/show_links.html', context_dict)

    else:
        form = GraphForm()
        context_dict['graph_form'] = form

    return render(request, 'linker/link_form.html', context_dict)


def show_mibig(request):
    context_dict = {}
    mb = MiBIG.objects.all()
    context_dict['mb'] = mb
    return render(request,'linker/mibig.html',context_dict)

def show_mibig_bgc(request,mibig_id):
    mibig = MiBIG.objects.get(id = mibig_id)
    context_dict = {}
    context_dict['mibig_bgc'] = mibig
    bgcs = mibig.bgc_set.all()
    gcfs = []
    for b in bgcs:
        gcfs.append(b.bgcgcf_set.all()[0].gcf)
    context_dict['bgcs'] = zip(bgcs,gcfs)
    return render(request,'linker/mibig_bgc.html',context_dict)

def showgcf(request,gcf_id):
    gcf = GCF.objects.get(id = gcf_id)
    context_dict = {}
    context_dict['gcf'] = gcf
    context_dict['strains'] = get_gcf_strain_set(gcf)
    context_dict['class_links'] = GCFtoClass.objects.filter(gcf = gcf)
    bgc = [b.bgc for b in gcf.bgcgcf_set.all()]
    strain = []
    for b in bgc:
        try:
            strain.append(b.bgcstrain_set.all()[0].strain)
        except:
            # doesnt have a strain -- probably from mibig
            strain.append(None)
    context_dict['bgc'] = zip(bgc,strain)

    context_dict['links'] = MFGCFEdge.objects.filter(gcf = gcf).order_by('p')
    context_dict['gcf_id'] = gcf.id
    context_dict['annotations'] = gcf.annotations.all()

    if request.method == 'POST':
        form = AnnotationForm(request.POST)
        if form.is_valid():

            # save the form
            annotation = form.cleaned_data['annotation']
            user = request.user
            user = User.objects.get(username="joewandy")
            gcf.annotations.create(message=annotation, user=user)

    form = AnnotationForm()
    context_dict['annotation_form'] = form
    return render(request,'linker/showgcf.html',context_dict)

def showmf(request,mf_id):
    mf = MF.objects.get(id = mf_id)
    context_dict = {}
    context_dict['mf'] = mf
    context_dict['strains'] = get_mf_strain_set(mf)
    spectra = [s.spectrum for s in mf.spectrummf_set.all()]
    spec_strains = []
    for s in spectra:
        spec_strains.append([st.strain for st in s.spectrumstrain_set.all()])
    context_dict['spectra'] = zip(spectra,spec_strains)
    
    links = MFGCFEdge.objects.filter(mf = mf).order_by('p')
    mibig = []
    for l in links:
        mibig.append(l.gcf.mibig)
    
    context_dict['links'] = zip(links,mibig)
    context_dict['mf_id'] = mf.id
    context_dict['annotations'] = mf.annotations.all()

    if request.method == 'POST':
        form = AnnotationForm(request.POST)
        if form.is_valid():

            # save the form
            annotation = form.cleaned_data['annotation']
            user = request.user
            user = User.objects.get(username="joewandy")
            mf.annotations.create(message=annotation, user=user)

    form = AnnotationForm()
    context_dict['annotation_form'] = form
    return render(request,'linker/showmf.html',context_dict)


def get_overlap_strain_set(gcf,mf):
    gcf_strains = get_gcf_strain_set(gcf)
    mf_strains = get_mf_strain_set(mf)
    overlap = gcf_strains.intersection(mf_strains)
    return overlap

def get_overlap_strains(request,gcf_id,mf_id):
    gcf = GCF.objects.get(id = gcf_id)
    mf = MF.objects.get(id = mf_id)
    
    overlap = get_overlap_strain_set(gcf,mf)
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


def get_families(families):
    gcftypes = []
    for i,g in enumerate(GCF_TYPES):
        po = len(GCF_TYPES) - 1 - i
        if families >= 2**po:
            gcftypes.append(g)
            families -= 2**po
    return gcftypes

def get_graph(request,analysis_id,metabanalysis_id,families,link_threshold):
    import networkx as nx
    from networkx.readwrite import json_graph

    analysis = Analysis.objects.get(id = analysis_id)
    metabanalysis = MetabAnalysis.objects.get(id = metabanalysis_id)
    G = nx.Graph()

    families = int(families)
    gcftypes = get_families(families)
    
    gcfclasses = []
    for g in gcftypes:
        gcfclasses.append(GCFClass.objects.get(name = g,source = 'BIGSCAPE'))

    mfs = MF.objects.filter(metabanalysis = metabanalysis)
    gcfs = GCF.objects.filter(analysis = analysis,gcftoclass__gcfclass__in = gcfclasses)
    # gcfs = GCF.objects.filter(analysis = analysis,gcftype__in = gcftypes)

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
    p_thresh = link_threshold
    links = MFGCFEdge.objects.filter(p__lte = p_thresh,mf__in = mfs,gcf__in = gcfs)
    links2 = MFGCFEdge.objects.filter(validated = True,mf__in = mfs,gcf__in = gcfs)
    links = list(set(list(links)+list(links2)))
    print "{},{},found {} links".format(analysis,metabanalysis,len(links))
    # links = list(set(links))
    with transaction.atomic():
        for link in links:
            if not link.mf.name in nodes:
                # n = len(get_mf_strain_set(link.mf))
                n = link.mf.n_strains
                if not n:
                    n = len(get_mf_strain_set(link.mf))
                    link.mf.n_strains = n
                    link.mf.save()
                # n = 10
                G.add_node(link.mf.name,nstrains = n,nodetype='mf',dbid = link.mf.id)
                nodes[link.mf.name] = True
            if not link.gcf.name in nodes:
                # n = len(get_gcf_strain_set(link.gcf))
                n = link.gcf.n_strains
                if not n:
                    n = len(get_gcf_strain_set(link.gcf))
                    link.gcf.n_strains = n
                    link.gcf.save()
                # n = 10
                gcftypes = link.gcf.gcftypeset
                overlap = list(set(gcfclasses).intersection(gcftypes))


                G.add_node(link.gcf.name,nstrains = n,gcftype = overlap[0].name,nodetype='gcf',dbid = link.gcf.id)
                nodes[link.gcf.name] = True

            G.add_edge(link.mf.name,link.gcf.name,weight =-np.log(link.p + 1e-10),validated = link.validated)
    

    
    return JsonResponse(json_graph.node_link_data(G))