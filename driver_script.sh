#!/bin/bash
#set env variables
DOWNLOAD_DIR=$1
THREADS=$2

#downlaod fasta and gtf files
python download_data.py DOWNLOAD_DIR

#unzip files
bash unzip_files.sh "$THREADS" "$DOWNLOAD_DIR"

#pull 16S sequences