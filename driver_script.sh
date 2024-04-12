#!/bin/bash
#set env variables
DOWNLOAD_DIR=$1
THREADS=$2

#build metadata file
if [ ! -f "$DOWNLOAD_DIR/genbank_assembly_metadata.tsv" ]; then
    echo -e "assembly\tgenbank_name\tlineage" > "$DOWNLOAD_DIR"/genbank_assembly_metadata.tsv
fi

#build sequence files
if [ ! -d "$DOWNLOAD_DIR/sequence_fastas" ]; then
    mkdir "$DOWNLOAD_DIR"/sequence_fastas/
    touch "$DOWNLOAD_DIR"/sequence_fastas/16S_sequence.fna "$DOWNLOAD_DIR"/sequence_fastas/16S_whole_scaffold.fna "$DOWNLOAD_DIR"/sequence_fastas/rps3_sequence.fna "$DOWNLOAD_DIR"/sequence_fastas/rps6_sequence.fna "$DOWNLOAD_DIR"/sequence_fastas/rps3_whole_scaffold.fna "$DOWNLOAD_DIR"/sequence_fastas/rps6_whole_scaffold.fna
fi

#downlaod fasta and gtf files
python download_genbank.py "$DOWNLOAD_DIR"

#extract lineage
for file in "$DOWNLOAD_DIR"/*_ani_report.txt; do
    python extract_lineage.py "$DOWNLOAD_DIR"/working_genbank_assembly_metadata.tsv "$file"
    echo "Processing file: $file"
done

#unzip files
bash unzip_files.sh "$THREADS" "$DOWNLOAD_DIR"

#pull 16S, rps3, and rps6 sequences
python pull_16S.py "$DOWNLOAD_DIR"
python pull_16S.py "$DOWNLOAD_DIR" --target_gene "30S ribosomal protein S3"
python pull_16S.py "$DOWNLOAD_DIR" --target_gene "30S ribosomal protein S6"

#merge files
tail -n +2 "$DOWNLOAD_DIR"/working_genbank_assembly_metadata.tsv >> "$DOWNLOAD_DIR"/genbank_assembly_metadata.tsv
cat "$DOWNLOAD_DIR"/working_sequence_fastas/16S_sequence.fna >> "$DOWNLOAD_DIR"/sequence_fastas/16S_sequence.fna
cat "$DOWNLOAD_DIR"/working_sequence_fastas/16S_whole_scaffold.fna >> "$DOWNLOAD_DIR"/sequence_fastas/16S_whole_scaffold.fna
cat "$DOWNLOAD_DIR"/working_sequence_fastas/rps3_whole_scaffold.fna >> "$DOWNLOAD_DIR"/sequence_fastas/rps3_whole_scaffold.fna
cat "$DOWNLOAD_DIR"/working_sequence_fastas/rps3_sequence.fna >> "$DOWNLOAD_DIR"/sequence_fastas/rps3_sequence.fna
cat "$DOWNLOAD_DIR"/working_sequence_fastas/rps6_sequence.fna >> "$DOWNLOAD_DIR"/sequence_fastas/rps6_sequence.fna
cat "$DOWNLOAD_DIR"/working_sequence_fastas/rps6_whole_scaffold.fna >> "$DOWNLOAD_DIR"/sequence_fastas/rps6_whole_scaffold.fna

#remove working files
rm "$DOWNLOAD_DIR"/working_genbank_assembly_metadata.tsv "$DOWNLOAD_DIR"/working_sequence_fastas/* "$DOWNLOAD_DIR"/md5checksums.txt "$DOWNLOAD_DIR"/*fna  "$DOWNLOAD_DIR"/*gtf "$DOWNLOAD_DIR"/*_ani_report.txt

