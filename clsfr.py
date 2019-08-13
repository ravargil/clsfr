import argparse
import os
import datetime
import classifier
from classifier import FilesClassifier
from classifier import ExifDateFilesSelector
import shutil


parser = argparse.ArgumentParser(description='Files classifier - reorganize files based on files\' date.')
parser.add_argument('--root-dir', required=True, help='the root dir to process all files')
parser.add_argument('--outdir', required=False, help='output dir to copy all files')
parser.add_argument('--strategy', choices=['year', 'month', 'day'], required=False, type=str, default='day', 
                    help='Strategy to classify files. Options are year|month|day. Default value is day')

args = parser.parse_args()

rootdir = args.root_dir
strategy = args.strategy

if ( (not os.path.isdir(rootdir)) or 
     (not os.path.exists(rootdir))):
    raise FileNotFoundError("No such directory: " + rootdir)
else:
    rootdir = os.path.abspath(rootdir)

outdir = rootdir #set default
if args.outdir: 
    outdir = args.outdir

if (not os.path.exists(outdir)):
    print ("Outdir " + outdir + " does not exist. Trying to create...")
    try:
        os.makedirs(outdir)
    except OSError as e:
        raise
else:
    outdir = os.path.abspath(outdir)


fs = ExifDateFilesSelector(args.strategy)
clsfr = FilesClassifier(fs)
clsfr.classify(rootdir)

for dir_name,file_path in clsfr:
    print ("{} {}".format(dir_name,file_path))
    destination_dir = outdir + "\\" + dir_name 
    base_name = os.path.basename(file_path)
    os.renames(file_path, destination_dir + "\\" + base_name)
