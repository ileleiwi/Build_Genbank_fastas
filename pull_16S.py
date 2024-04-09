from Bio import SeqIO
import argparse
import os

parser = argparse.ArgumentParser(description="Extract sequences from GTF and FASTA files")
parser.add_argument("working_dir", help="Path to directory containing the GTF and FASTA files")
parser.add_argument("--target_gene", default="16S ribosomal RNA", help="Target gene to search for in the GTF file")
args = parser.parse_args()

def get_filenames(working_dir):
    files = os.listdir(working_dir)
    file_names = [file[:-4] for file in files if file.endswith('.fna')]
    return file_names

def extract_coords_from_gtf(gtf_file, target_gene):
    name_coords = {}
    with open(gtf_file, 'r') as gtf:
        for line in gtf:
            if target_gene in line:
                fields = line.strip().split('\t')
                scaffold_name = fields[0]
                start_coordinate = int(fields[3])  # start coordinate is in column 4
                end_coordinate = int(fields[4])    # end coordinate is in column 5
                name_coords.setdefault(scaffold_name, []).append((start_coordinate, end_coordinate))
    return name_coords

def extract_sequences_from_fasta_with_coords(fasta_file, scaffold_coords):
    sequences_with_coords = {}
    for record in SeqIO.parse(fasta_file, 'fasta'):
        if record.id in scaffold_coords:
            coords = scaffold_coords[record.id]
            for idx, coord in enumerate(coords):
                start_coord, end_coord = coord
                sequence = str(record.seq)[start_coord - 1:end_coord] 
                sequences_with_coords.setdefault(record.id, []).append(sequence)
    return sequences_with_coords

def extract_whole_sequences_from_fasta(fasta_file, scaffold_names):
    sequences = {}
    for record in SeqIO.parse(fasta_file, 'fasta'):
        if record.id in scaffold_names:
            sequences[record.id] = str(record.seq)
    return sequences

def extract_scaffold_headers_from_fasta(fasta_file):
    scaffold_headers = {}
    for record in SeqIO.parse(fasta_file, 'fasta'):
        scaffold_headers[record.id] = record.description.split(' ', 1)[1]
    return scaffold_headers


def write_fasta(output_file, retrieved_sequences, file_name, out_type, scaffold_headers):
    if out_type == "16S":
        with open(output_file, 'a') as output:
            for name, sequences in retrieved_sequences.items():
                # Check if there are sequences associated with the scaffold
                if sequences:
                    # Take the first sequence from the list
                    sequence = sequences[0]
                    original_scaff_header = scaffold_headers.get(name, name)
                    output.write(f'>{file_name} | {name} | {original_scaff_header}\n{sequence}\n')
    elif out_type == "whole":
        with open(output_file, 'a') as output:
            for name, sequence in retrieved_sequences.items():
                original_scaff_header = scaffold_headers.get(name, name)
                output.write(f'>{file_name} | {name} | {original_scaff_header}\n{sequence}\n')



output_dir = os.path.join(args.working_dir, 'sequence_fastas')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file_with_coords = os.path.join(output_dir, '16S_sequence.fna')
output_file_whole = os.path.join(output_dir, '16S_whole_scaffold.fna')

if not os.path.exists(output_file_with_coords):
    open(output_file_with_coords, 'w').close()

if not os.path.exists(output_file_whole):
    open(output_file_whole, 'w').close()

for file_name in get_filenames(args.working_dir):
    gtf_file = os.path.join(args.working_dir, f'{file_name}.gtf')
    fasta_file = os.path.join(args.working_dir, f'{file_name}.fna')
    
    scaffold_coords = extract_coords_from_gtf(gtf_file, args.target_gene)
    scaffold_headers = extract_scaffold_headers_from_fasta(fasta_file)

    if scaffold_coords:
        sequences_with_coords = extract_sequences_from_fasta_with_coords(fasta_file, scaffold_coords)
        sequences = extract_whole_sequences_from_fasta(fasta_file, scaffold_coords)

        write_fasta(output_file_with_coords, sequences_with_coords, file_name=file_name, out_type="16S", scaffold_headers=scaffold_headers)
        write_fasta(output_file_whole, sequences, file_name=file_name, out_type="whole", scaffold_headers=scaffold_headers)
