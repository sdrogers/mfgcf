import argparse
import csv
import glob
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import django
django.setup()

STRAIN_LIST = ['CNB091','CNB440','CNB458','CNB476','CNB527','CNB536','CNH099','CNH189','CNH287','CNH643','CNH646','CNH713','CNH718','CNH732','CNH877','CNH898','CNH905','CNH941','CNH962','CNH963','CNH964','CNH996','CNP082','CNP105','CNP193','CNQ149','CNQ329','CNQ525','CNQ748','CNQ766','CNQ768','CNQ865','CNQ884','CNR107','CNR114','CNR425','CNR510','CNR698','CNR699','CNR894','CNR909','CNR921','CNR942','CNS051','CNS055','CNS103','CNS143','CNS197','CNS205','CNS237','CNS243','CNS296','CNS299','CNS325','CNS335','CNS342','CNS416','CNS606','CNS615','CNS654','CNS673','CNS744','CNS801','CNS820','CNS848','CNS860','CNS863','CNS960','CNS991','CNS996','CNT001','CNT003','CNT005','CNT029','CNT045','CNT084','CNT088','CNT124','CNT131','CNT133','CNT138','CNT148','CNT150','CNT250','CNT261','CNT302','CNT318','CNT360','CNT371','CNT372','CNT403','CNT569','CNT584','CNT603','CNT609','CNT796','CNT798','CNT799','CNT800','CNT849','CNT850','CNT851','CNT854','CNT855','CNT857','CNT859','CNX435','CNX481','CNX482','CNX508','CNX814','CNX891','CNY011','CNY012','CNY202','CNY228','CNY230','CNY231','CNY234','CNY237','CNY239','CNY243','CNY244','CNY256','CNY260','CNY280','CNY281','CNY282','CNY330','CNY331','CNY363','CNY486','CNY498','CNY646','CNY666','CNY673','CNY678','CNY679','CNY681','CNY685','CNY690','CNY694','CNY703',]
MEDIA_LIST = ['ETHYLACETATE','METHANOL','BUTANOL']
from linker.models import *


from django.db import transaction

from pyteomics import mgf

strain_id_file = 'strain_ids.csv'


def read_mgf(filepath):
    data = {}
    with mgf.read(filepath) as reader:
        for entry in reader:
            entry_id = entry['params']['scans']
            entry_id = str(entry_id)
            if entry_id in data:
                raise KeyError('Duplicate scan ID: %s' % entry_id)
            else:
                data[entry_id] = entry
    return data


def load_ms_peaks(filepath):
    data = read_mgf(filepath)
    peaks = {}
    for scan_id, scan_data in data.items():
        peaks[str(scan_id)] = zip(scan_data['m/z array'], scan_data['intensity array'])
    return peaks


# ??
def get_strain(accession,strain_dir):
    if not accession.startswith('unknown'):
        path2files = os.path.join(strain_dir,accession+'.*')
        filelist = glob.glob(path2files)
        # print filelist
        if not len(filelist) == 1:
            print accession
            print filelist
        else:
            filelist = filelist[0]
            ftype = filelist.split('.')[-1]
            if ftype == 'gb' or ftype == 'gbff':
                with open(filelist,'r') as f:
                    for line in f:
                        if line.startswith('SOURCE'):
                            strain = line.split()[-1]
                            return strain
            elif ftype == 'gbk':
                with open(filelist,'r') as f:
                    for line in f:
                        tokens = line.split()
                        if tokens[0].startswith('/organism'):
                            strain = tokens[-1][:-1]
                            return strain
            elif ftype == 'fna':
                with open(filelist,'r') as f:
                    headline = f.next()
                    strain = headline.split()[3]
                    return strain

            else:
                print ftype,"Unknown file type!"

                
    return None


# load mf file in gnps format
def load_mf_file(mf_file, peak_dict, metabanalysis):
    mfdict = {}
    singleton_count = 0
    with transaction.atomic():
        with open(mf_file, 'r') as f:
            reader = csv.reader(f, dialect='excel', delimiter='\t')
            heads = reader.next()

            libpos = heads.index('LibraryID')
            linkpos = heads.index('ProteoSAFeClusterLink')
            mfpos = heads.index('componentindex')  # sometimes this is ComponentIndex?!
            ppos = heads.index('parent mass')
            prpos = heads.index('precursor mass')
            spectrum_pos = heads.index('cluster index')

            strain_index_dict = {}
            strain_dict = {}

            for strain_name in STRAIN_LIST:
                try:
                    strain_pos = heads.index(strain_name)
                    strain_index_dict[strain_name] = heads.index(strain_name)
                    strain, _ = Strain.objects.get_or_create(name=strain_name)
                    strain_dict[strain_name] = strain
                except:
                    pass

            media_index_dict = {}
            media_dict = {}
            for media_name in MEDIA_LIST:
                # try:
                    media_index_dict[media_name] = heads.index(media_name)
                    media, _ = Media.objects.get_or_create(name=media_name, metabanalysis=metabanalysis)
                    media_dict[media_name] = media
                # except:
                #     pass

            lines_read = 0
            for line in reader:
                if len(line[1]) == 0:  # overcome weird lines at bottom
                    continue
                suid = line[0]
                spectrum, created = Spectrum.objects.get_or_create(rowid=suid, metabanalysis=metabanalysis)
                if created:
                    spectrum.libraryid = line[libpos]
                    spectrum.link = line[linkpos]
                    spectrum.parentmass = float(line[ppos])
                    spectrum.precursormass = float(line[prpos])
                    spectrum.save()

                Peak.objects.filter(spectrum=spectrum).delete()

                spectrum_id = line[spectrum_pos]
                if peak_dict is not None:
                    peaks = peak_dict[str(spectrum_id)]
                    for position, intensity in peaks:
                        Peak.objects.create(spectrum=spectrum, position=position, intensity=intensity)

                mfnumber = line[mfpos]
                if not len(mfnumber) == 0 and not mfnumber == '-1':
                    mfname = 'MF_{}'.format(mfnumber)
                    if mfname not in mfdict:
                        mf, created = MF.objects.get_or_create(name=mfname, metabanalysis=metabanalysis)
                        mfdict[mfname] = mf
                    else:
                        mf = mfdict[mfname]
                    SpectrumMF.objects.get_or_create(spectrum=spectrum, mf=mf)
                else:
                    # singleton - still save but have to make a special name
                    mfname = 'MF_S_{}'.format(singleton_count)
                    singleton_count += 1
                    mf,created = MF.objects.get_or_create(name=mfname, metabanalysis=metabanalysis)
                    mfdict[mfname] = mf
                    SpectrumMF.objects.get_or_create(spectrum=spectrum, mf=mf)

                for strain_name in strain_index_dict:
                    count = int(line[strain_index_dict[strain_name]])
                    if count > 0:
                        SpectrumStrain.objects.get_or_create(spectrum=spectrum,
                                                             strain=strain_dict[strain_name],
                                                             count=int(line[strain_index_dict[strain_name]]))

                for media_name in media_index_dict:
                    SpectrumMedia.objects.get_or_create(spectrum=spectrum,
                                                        media=media_dict[media_name],
                                                        count=int(line[media_index_dict[media_name]]))

                lines_read += 1
                if lines_read % 100 == 0:
                    print "Read {}".format(lines_read)


def remove_things(analysis):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load MS analysis into database')
    parser.add_argument('metabname', help='MS analysis name')
    parser.add_argument('mffile', help='GPNS file')
    parser.add_argument('spectra', help='MGF file', nargs='?', default=None)
    args = parser.parse_args()

    metabanalysis_name = args.metabname
    mf_file = args.mffile
    mgf_file = args.spectra

    try:
        metabanalysis = MetabAnalysis.objects.create(name=metabanalysis_name)
    except:
        print "Analysis already exists"
        metabanalysis = MetabAnalysis.objects.get(name=metabanalysis_name)
        # remove_things(analysis)

    if args.spectra:
        peak_dict = load_ms_peaks(mgf_file)
    else:
        peak_dict = None

    load_mf_file(mf_file, peak_dict, metabanalysis)
