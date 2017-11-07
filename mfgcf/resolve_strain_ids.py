#!/usr/bin/python

import glob
import os
import sys


def get_strain_gb(filename):
    """
    Parse .gb or .gbff files
    """
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('SOURCE'):
                strain = line.split()[-1]
                return strain


def get_strain_gbk(filename):
    """
    Parse .gbk files
    """
    with open(filename, 'r') as f:
        for line in f:
            tokens = line.split()
            if tokens[0].startswith('/organism'):
                strain = tokens[-1][:-1]
                return strain


def get_strain_fna(filename):
    """
    Parse .fna files (dubious..)
    """
    with open(filename, 'r') as f:
        headline = f.next()
        # Not reliable!
        strain = headline.split()[3]
        return strain


def get_strain_file(filename):
    """
    Try to parse based on file ending
    """
    ftype = filename.split('.')[-1]
    if ftype == 'gb' or ftype == 'gbff':
        strain = get_strain_gb(filename)
    elif ftype == 'gbk':
        strain = get_strain_gbk(filename)
    elif ftype == 'fna':
        strain = get_strain_fna(filename)
    else:
        raise IOError("Unknown file type: %s" % ftype)

    return strain


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Try to extract strain IDs from raw data files (.gb, .gbff, .gbk, .fna)"
        print "Usage: %s <path>" % sys.argv[0]
        raise SystemExit

    datadir = sys.argv[1]

    for line in glob.glob(os.path.join(datadir, '*')):
        if line.startswith('.') or line.endswith('zip'):
            pass
        else:
            strain = get_strain_file(line)
            filename = os.path.basename(line).split('.')[0]
            print '%s,%s' % (filename, strain)
