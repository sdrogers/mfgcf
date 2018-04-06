import argparse
import csv
import glob

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mfgcf.settings")

import django
django.setup()

from django.db import transaction
from linker import models

import linker


def process_shift_file(filename, source, label_column_idx, shift_column_idx):
    print 'Processing %s' % filename
    with transaction.atomic():
        with open(filename, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            head = reader.next()
            for fields in reader:
                label = fields[label_column_idx].lower()
                shift = float(fields[shift_column_idx])
                print "Adding shift: Type %s, name %s, shift %s" % (source, label, shift)
                if models.Shift.objects.filter(source=source, name=label).exists():
                    shift_object = models.Shift.objects.get(source=source, name=label)
                    shift_object.shift = shift
                    shift_object.save()
                else:
                    shift_object = models.Shift.objects.get_or_create(source=source, name=label, shift=shift)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load .csv file with mass shifts into database")
    parser.add_argument("-l", dest="label", help="Index of label column (0-based)", required=True, type=int)
    parser.add_argument("-s", dest="shift", help="Index of shift column (0-based)", required=True, type=int)
    parser.add_argument("source", help="Data source")
    parser.add_argument("inputpath", help="Directory containing csv aa prediction files")
    args = parser.parse_args()

    inputpath = args.inputpath
    label_idx = args.label
    shift_idx = args.shift
    source = args.source

    process_shift_file(inputpath, source, label_idx, shift_idx)
