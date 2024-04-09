#!/bin/bash
#set env variables
DOWNLOAD_DIR=$1
THREADS=$2

#downlaod fasta and gtf files
python download_data.py "$DOWNLOAD_DIR"

#unzip files
bash unzip_files.sh "$THREADS" "$DOWNLOAD_DIR"

#pull 16S, rps3, and rps6 sequences
python pull_16S.py "$DOWNLOAD_DIR"
python pull_16S.py "$DOWNLOAD_DIR" --target_gene "30S ribosomal protein S3"
python pull_16S.py "$DOWNLOAD_DIR" --target_gene "30S ribosomal protein S6"