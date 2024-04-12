import os
import argparse
import pandas as pd
import re
import numpy as np

def extract_lineage_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            text = file.read()
            return extract_lineage(text)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

def extract_lineage(text):
    # Find the line starting with "Best match:"
    match_line = re.search(r"Best match:.*", text)
    if match_line:
        # Extract the lineage information using regex
        lineage_match = re.search(r"lineage = (.+?)\)", match_line.group())
        if lineage_match:
            return lineage_match.group(1), "(Best match)"
    
    # If lineage not found in "Best match" line, try "Submitted organism" line
    submitted_organism_line = re.search(r"Submitted organism:.*", text)
    if submitted_organism_line:
        lineage_match = re.search(r"lineage = (.+?)\)", submitted_organism_line.group())
        if lineage_match:
            return lineage_match.group(1), "(Submitted organism)"
    
    return None, None

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Update lineage information in a TSV file")
parser.add_argument("tsv_file", help="Path to the TSV file")
parser.add_argument("text_file", help="Path to the text file containing lineage information")
args = parser.parse_args()

# Read the TSV file
tsv_file_path = args.tsv_file
if not os.path.isfile(tsv_file_path):
    print(f"Error: File '{tsv_file_path}' not found.")
    exit()

df = pd.read_csv(tsv_file_path, sep='\t')

# Extract the prefix from the text file name
text_file_name = os.path.basename(args.text_file)
prefix = text_file_name.split('_ani_report.txt')[0]

# Read the text file containing lineage information
text_file_path = args.text_file
if not os.path.isfile(text_file_path):
    print(f"Error: File '{text_file_path}' not found.")
    exit()

lineage, source = extract_lineage_from_file(text_file_path)

if lineage:
    # Update the 'lineage' column in the DataFrame where 'assembly' column matches the prefix
    mask = df['assembly'].str.startswith(prefix)
    new_lineage_values = [lineage + ' ' + source if m else np.nan for m in mask]
    df['lineage'] = np.where(mask, new_lineage_values, df['lineage'])

    # Save the updated DataFrame to the same location
    df.to_csv(tsv_file_path, sep='\t', index=False)
    print(f"Updated TSV file saved to {tsv_file_path}")
else:
    print("Error: Lineage information not found in the text file.")
