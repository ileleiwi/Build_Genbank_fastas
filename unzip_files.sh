#!/bin/bash

NUM_THREADS=$1
INPUT_DIR=$2

if [ -z "$NUM_THREADS" ] || [ -z "$INPUT_DIR" ]; then
    echo "Usage: $0 <NUM_THREADS> <INPUT_DIR>"
    exit 1
fi

if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: INPUT_DIR '$INPUT_DIR' does not exist."
    exit 1
fi
for gz_file in $INPUT_DIR/*.gz; do
    output_file="${gz_file%.gz}"
    pigz -d -p "$NUM_THREADS" -c "$gz_file" > "$output_file"
    echo "Unzipped $gz_file"
    rm "$gz_file"
done

echo "All files unzipped successfully."
