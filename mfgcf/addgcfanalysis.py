import os,sys,csv
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import django
django.setup()

GCF_TYPES = ['allRiPPs','allPKSother','allOthers','allNRPS','allPKSI','allPKS-NRP_Hybrids','allSaccharides','allTerpene']
GCF_TYPES2 = ['All_RiPPs','All_PKSother','All_Others','All_NRPS','All_PKSI','All_PKS-NRP_Hybrids','All_Saccharides','All_Terpene']

STRAIN_LIST = ['CNB091','CNB440','CNB458','CNB476','CNB527','CNB536','CNH099','CNH189','CNH287','CNH643','CNH646','CNH713','CNH718','CNH732','CNH877','CNH898','CNH905','CNH941','CNH962','CNH963','CNH964','CNH996','CNP082','CNP105','CNP193','CNQ149','CNQ329','CNQ525','CNQ748','CNQ766','CNQ768','CNQ865','CNQ884','CNR107','CNR114','CNR425','CNR510','CNR698','CNR699','CNR894','CNR909','CNR921','CNR942','CNS051','CNS055','CNS103','CNS143','CNS197','CNS205','CNS237','CNS243','CNS296','CNS299','CNS325','CNS335','CNS342','CNS416','CNS606','CNS615','CNS654','CNS673','CNS744','CNS801','CNS820','CNS848','CNS860','CNS863','CNS960','CNS991','CNS996','CNT001','CNT003','CNT005','CNT029','CNT045','CNT084','CNT088','CNT124','CNT131','CNT133','CNT138','CNT148','CNT150','CNT250','CNT261','CNT302','CNT318','CNT360','CNT371','CNT372','CNT403','CNT569','CNT584','CNT603','CNT609','CNT796','CNT798','CNT799','CNT800','CNT849','CNT850','CNT851','CNT854','CNT855','CNT857','CNT859','CNX435','CNX481','CNX482','CNX508','CNX814','CNX891','CNY011','CNY012','CNY202','CNY228','CNY230','CNY231','CNY234','CNY237','CNY239','CNY243','CNY244','CNY256','CNY260','CNY280','CNY281','CNY282','CNY330','CNY331','CNY363','CNY486','CNY498','CNY646','CNY666','CNY673','CNY678','CNY679','CNY681','CNY685','CNY690','CNY694','CNY703',]
MEDIA_LIST = ['ETHYLACETATE','METHANOL','BUTANOL']
from linker.models import *

import glob

from django.db import transaction

strain_id_file = 'strain_ids.csv'

def load_gcf_trio(analysis,file_trio,strain_dict):
    network_file,tsv_file,annotations_file = file_trio
    # This file includes the BGC info
    bgc_dict = {}
    with transaction.atomic():
        with open(annotations_file,'r') as f:
            reader = csv.reader(f,delimiter='\t')
            heads = reader.next()
            for line in reader:
                name = line[0]  
                bgc,_ = BGC.objects.get_or_create(name = name,analysis=analysis)
                bgc.accession = line[1]
                bgc.description = line[2]
                bgc.product = line[3]
                bgc.bgsclass = line[4]
                bgc.save()
                bgc_dict[bgc.name] = bgc
                genbank_name = bgc.name.split('_')[0]
                if '.' in genbank_name:
                    genbank_name = genbank_name.split('.')[0]
                if genbank_name == 'GCA':
                    # hack!
                    genbank_name = '_'.join(bgc.name.split('_')[:2])
                    genbank_name = genbank_name.split('.')[0]
                strain_name = None
                migbig = None
                if not genbank_name in strain_dict:
                    print "{} STRAIN NOT FOUND!".format(genbank_name)
                    # check if it is a bgc
                    try:
                    	mibig = MiBIG.objects.get(name = genbank_name)
                    	bgc.mibig = mibig
                    	bgc.save()
                    	print "\t its from MiBIG!"
                    except:
                    	pass
                else:
                    strain_name = strain_dict[genbank_name]
                if not strain_name == None:
                    strain,created = Strain.objects.get_or_create(name = strain_name)
                    if created:
                        strain.organism = line[5]
                        strain.taxonomy = line[6]
                        strain.save()
                    BGCStrain.objects.get_or_create(bgc = bgc,strain = strain)

            
    
    # with open(network_file,'r') as f:
    #   for line in f:
    #       print line
    #       break
    with open(tsv_file,'r') as f:
        with transaction.atomic():
            reader = csv.reader(f,delimiter = '\t')
            heads = reader.next()
            gcf_type = tsv_file.split(os.sep)[-1].split('_')[0]
            gcf_dict = {}
            for line in reader:
                bgcname = line[0]
                bgc = BGC.objects.get(name = bgcname,analysis = analysis)
                family_number = line[1]
                family_name = 'GCF_{}_{}'.format(gcf_type,family_number)
                if not family_name in gcf_dict:
                    gcf,created = GCF.objects.get_or_create(name = family_name,analysis = analysis)
                    if created:
                        gcf.gcftype = gcf_type
                        gcf.save()
                    gcf_dict[family_name] = gcf
                else:
                    gcf = gcf_dict[family_name]

                BGCGCF.objects.get_or_create(bgc = bgc,gcf = gcf)
    return strain_dict
    



def get_files(bigscape_outout_dir):
    # Get the trios of files from the output dir
    file_trios = []
    for i,t in enumerate(GCF_TYPES):
        network_file = glob.glob(os.path.join(bigscape_outout_dir,t+'*.network'))
        if len(network_file) == 1:
            network_file = network_file[0]
            sub_name = ".".join(network_file.split(os.sep)[-1].split('.')[:-1])
            last_bit = sub_name.split('_')[-1]
            tsv_file = os.path.join(bigscape_outout_dir,t+'_clustering_'+ last_bit +'.tsv')
            annotations_file = os.path.join(bigscape_outout_dir,'Network_Annotations_'+GCF_TYPES2[i]+'.tsv')
            file_trios.append((network_file,tsv_file,annotations_file))
    return file_trios
    


if __name__ == '__main__':
    analysis_name = sys.argv[1]
    bigscape_outout_dir = sys.argv[2]
   
   
    try:
        analysis = Analysis.objects.create(name = analysis_name)
    except:
        print "Analysis already exists"
        analysis = Analysis.objects.get(name = analysis_name)

    
    file_trios = get_files(bigscape_outout_dir)
    strain_dict = {}

    with open(strain_id_file,'r') as f:
        reader = csv.reader(f)
        for line in reader:
            strain_dict[line[0]] = line[1]
    for file_trio in file_trios:
        print "Adding BGCs (and strains) from {}".format(file_trio[0])
        strain_dict = load_gcf_trio(analysis,file_trio,strain_dict)


    






