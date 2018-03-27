import argparse
import csv
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")
import glob

import django
django.setup()

from django.db import transaction

from linker.models import *


GCF_TYPES = ['allRiPPs',
             'allPKSother',
             'allOthers',
             'allNRPS',
             'allPKSI',
             'allPKS-NRP_Hybrids',
             'allSaccharides',
             'allTerpene']

GCF_TYPES2 = ['All_RiPPs',
              'All_PKSother',
              'All_Others',
              'All_NRPS',
              'All_PKSI',
              'All_PKS-NRP_Hybrids',
              'All_Saccharides',
              'All_Terpene']

# strain_ids.csv maps all the various ids to genbank ids
strain_id_file = 'strain_ids.csv'


def preprocess_genbank_name(string):
                genbank_name = string.split('_')[0]
                if '.' in genbank_name:
                    genbank_name = genbank_name.split('.')[0]
                if genbank_name == 'GCA':
                    # hack!
                    genbank_name = '_'.join(string.split('_')[:2])
                    genbank_name = genbank_name.split('.')[0]
                return genbank_name


def string_to_genbank(genbank_name):
    strain_name = None
    if genbank_name in strain_dict:
        strain_name = strain_dict[genbank_name]
    else:
        print "{} STRAIN NOT FOUND!".format(genbank_name)
    return strain_name


def string_to_mibig(genbank_name):
    mibig = None
    # check if it is a bgc
    try:
        mibig = MiBIG.objects.get(name=genbank_name)
        print "\t its from MiBIG!"
    except:
        pass
    return mibig


def load_gcf_trio(analysis, family_file, annotations_file, strain_dict, gcf_type=None):
    # This file includes the BGC info
    bgc_dict = {}
    with transaction.atomic():
        with open(annotations_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            heads = reader.next()
            for line in reader:
                name = line[0]
                bgc, _ = BGC.objects.get_or_create(name=name, analysis=analysis)
                bgc.accession = line[1]
                bgc.description = line[2]
                bgc.product = line[3]
                bgc.bgsclass = line[4]
                bgc.save()
                bgc_dict[bgc.name] = bgc

                genbank_string = preprocess_genbank_name(bgc.name)
                strain_name = string_to_genbank(genbank_string)

                if strain_name is not None:
                    strain, created = Strain.objects.get_or_create(name=strain_name)
                    if created:
                        strain.organism = line[5]
                        strain.taxonomy = line[6]
                        strain.save()
                    BGCStrain.objects.get_or_create(bgc=bgc, strain=strain)
                else:
                    mibig = string_to_mibig(genbank_string)
                    if mibig is not None:
                        bgc.mibig = mibig
                        bgc.save()

    # with open(network_file,'r') as f:
    #   for line in f:
    #       print line
    #       break
    with open(family_file, 'r') as f:
        with transaction.atomic():
            reader = csv.reader(f, delimiter='\t')
            heads = reader.next()
            if gcf_type is None:
                gcf_type = family_file.split(os.sep)[-1].split('_')[0]
            gcf_dict = {}
            for line in reader:
                bgcname = line[0]
                bgc = BGC.objects.get(name=bgcname, analysis=analysis)
                family_number = line[1]
                family_name = 'GCF_{}_{}'.format(gcf_type, family_number)
                if family_name not in gcf_dict:
                    gcf, created = GCF.objects.get_or_create(name=family_name, analysis=analysis)
                    if created:
                        # add type
                        gcfclass, class_created = GCFClass.objects.get_or_create(name=gcf_type)
                        # link gcftype and gcf
                        gcflink, link_created = GCFtoClass.objects.get_or_create(gcf=gcf, gcfclass=gcfclass)
                        if class_created:
                            gcfclass.source = 'BIGSCAPE'
                            gcfclass.save()
                        if link_created:
                            gcflink.save()
                        gcf.save()
                    gcf_dict[family_name] = gcf
                else:
                    gcf = gcf_dict[family_name]

                BGCGCF.objects.get_or_create(bgc=bgc, gcf=gcf)
    return strain_dict


def get_files(bigscape_outout_dir):
    # Get the trios of files from the output dir
    file_trios = []
    for i, t in enumerate(GCF_TYPES):
        network_file = glob.glob(os.path.join(bigscape_outout_dir, t + '*.network'))
        if len(network_file) == 1:
            network_file = network_file[0]
            sub_name = ".".join(network_file.split(os.sep)[-1].split('.')[:-1])
            last_bit = sub_name.split('_')[-1]
            tsv_file = os.path.join(bigscape_outout_dir, t + '_clustering_' + last_bit + '.tsv')
            annotations_file = os.path.join(bigscape_outout_dir, 'Network_Annotations_' + GCF_TYPES2[i] + '.tsv')
            file_trios.append((network_file, tsv_file, annotations_file))
    return file_trios


def get_strain_dict():
    """
    Load strain names
    """
    strain_dict = {}
    with open(strain_id_file, 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            strain_dict[line[0]] = line[1]

    # add null mappings (if the strain IDs are correct to begin with)
    for strain_id in strain_dict.values():
        strain_dict[strain_id] = strain_id

    return strain_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import GCF results into database')
    parser.add_argument('name', help='Analysis name')
    parser.add_argument('family', help='Family .tsv file')
    parser.add_argument('annotations', help='BGC annotations file')
    parser.add_argument('-t', dest='type', help='BGC type', default=None)
    args = parser.parse_args()

    analysis_name = args.name
    family_file = args.family
    annotations_file = args.annotations
    bgc_type = args.type

    strain_dict = get_strain_dict()

    try:
        analysis = Analysis.objects.create(name=analysis_name)
    except django.db.utils.IntegrityError:
        print "Analysis already exists"
        analysis = Analysis.objects.get(name=analysis_name)

    # list of (network file, tsv clustering file, network annotation file) tuples
    # network file            - contains detailed info about the links btw. BGCs (incl. individual weights)
    # tsv clustering file     - BGC : family pairs
    # network annotation file - individual BGC annotations
    # file_trios = get_files(bigscape_outout_dir)

    print "Adding BGCs (and strains) from {}".format(family_file)
    strain_dict = load_gcf_trio(analysis, family_file, annotations_file, strain_dict, bgc_type)
