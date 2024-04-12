import ftputil
import os 
import logging
import time
import hashlib
import argparse

#TODO integrate into a pipeline that stops after all the genomes within a bacteria dir are downloaded and pulls out 16S, rps3 and rps6 sequences then saves them to individual fastas with the genus and genbank name and gene as sequence header

parser = argparse.ArgumentParser(description="Download files from Genbank server")
parser.add_argument("local_dir", help="working directory")
args = parser.parse_args()

#"/Users/leleiwi1/Desktop/LLNL_postdoc/kmer_tool_16S/16S_rRNA/dl_dir"
local_dir = args.local_dir

error_log_file = os.path.join(local_dir, "ftp_errors.log")
logging.basicConfig(filename=error_log_file, level=logging.ERROR)


# Genome Log file
genome_log = local_dir + "/genome.log"

# subdir Log file
genome_subdir_log = local_dir +  "/dl_subdir.log"

# DL log file
success_log = local_dir +  "/progress.log"

# MD5 checksum file
md5_file = local_dir + "/md5checksums.txt"

# TSV file
tsv_file = local_dir + "/genbank_assembly_metatdata.tsv"

def read_log_file(log_type):
    if log_type == "genome":
        if not os.path.exists(genome_log):
            return set()
        with open(genome_log, "r") as f:
            return set(f.read().splitlines())
    if log_type == "subdir_dl":
        if not os.path.exists(genome_subdir_log):
            return set()
        with open(genome_subdir_log, "r") as f:
            return set(f.read().splitlines())
    if log_type == "success":
        if not os.path.exists(success_log):
            return set()
        with open(success_log, "r") as f:
            return set(f.read().splitlines())


def write_log_file(log_type, file_name):
    if log_type == "genome":
        with open(genome_log, "a") as f:
            f.write(file_name + "\n")
    if log_type == "subdir_dl":
        with open(genome_subdir_log, "a") as f:
            f.write(file_name + "\n")
    if log_type == "success":
        with open(success_log, "a") as f:
            f.write(file_name + "\n")

def calculate_md5(file_path):
    with open(file_path, "rb") as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def verify_checksums(local_file_path, file_type):
    local_md5_file = os.path.join(local_dir, "md5checksums.txt")
    
    with open(local_md5_file, "r") as f:
        for line in f:
            checksum, file_path = line.strip().split(maxsplit=1)
            if file_type in file_path:  
                local_checksum = calculate_md5(local_file_path)
                
                if checksum == local_checksum:
                    print(f"Checksum matched for {file_path}")
                    return True
                else:
                    print(f"Checksum mismatch for {file_path}")
                    return False

def write_metadata(assembly, genbank_name, lineage):
    if not os.path.exists(tsv_file):
        with open(tsv_file, "w") as f:
            f.write(f"assembly\tgenbank_name\tlineage\n{assembly}\t{genbank_name}\t{lineage}\n")
    else: 
        with open(tsv_file, "a") as f:
            f.write(f"{assembly}\t{genbank_name}\t{lineage}\n")


class MyFTPHost(ftputil.FTPHost):
    def _log(self, cmd, result):
        if result.startswith("4") or result.startswith("5"):
            logging.error("FTP command failed: %s", cmd)
            logging.error("Error message: %s", result)
        else:
            print("Sent:", cmd)
            print("Received:", result)

# FTP server details
ftp_host = "ftp.ncbi.nlm.nih.gov"
ftp_dir = "/genomes/genbank/bacteria/"

# Connect to server
with MyFTPHost(ftp_host, "anonymous", "anonymous@", timeout=60) as ftp:
    ftp.use_passive_mode = True
    ftp.chdir(ftp_dir)
    print("FTP connection successful.")
    files = ftp.listdir(ftp.curdir)
    for item in files:
        if item not in read_log_file(log_type="genome"):
            if ftp.path.isdir(item):
                print("Working on:", item)
                ftp.chdir(item)
                if ftp.path.isdir("latest_assembly_versions"):
                    ftp.chdir("latest_assembly_versions")
                    dir_files = ftp.listdir(ftp.curdir)
                    len_dir = len(dir_files)
                    print(len_dir)
                    item_check = 0
                    for file in dir_files:
                        if file not in read_log_file(log_type="subdir_dl"):
                            if not ftp.path.exists(file):
                                logging.error("Directory does not exist: %s", file)
                                item_check += 1
                                ftp.chdir(ftp_dir + item + "/latest_assembly_versions")
                                continue
                            ftp.chdir(file)
                            ftp.download("md5checksums.txt", md5_file)
                            file_name_fna = file + "_genomic.fna.gz"
                            file_name_gtf = file + "_genomic.gtf.gz"
                            file_name_ani = file + "_ani_report.txt"
                            genomic_fna_check = 0
                            genomic_gtf_check = 0
                            # Download genomic.gtf.gz
                            try:
                                if file_name_gtf in ftp.listdir(ftp.curdir) and file_name_gtf not in read_log_file(log_type="success"):
                                    local_path_gtf = os.path.join(local_dir, file_name_gtf)
                                    ftp.download_if_newer(file_name_gtf, local_path_gtf)
                                    genomic_gtf_check += 1
                                    write_log_file(log_type="success", file_name=file_name_gtf)
                                    # Download genomic.fna.gz
                                    if file_name_fna in ftp.listdir(ftp.curdir) and read_log_file(log_type="success"):
                                        local_path_fna = os.path.join(local_dir, file_name_fna)
                                        ftp.download_if_newer(file_name_fna, local_path_fna)
                                        genomic_fna_check += 1
                                        write_log_file(log_type="success", file_name=file_name_fna)
                                    # Download ani_report.txt
                                    if file_name_ani in ftp.listdir(ftp.curdir) and read_log_file(log_type="success"):
                                        local_path_ani = os.path.join(local_dir, file_name_ani)
                                        ftp.download_if_newer(file_name_ani, local_path_ani)
                                        
                                        
                                else:
                                    print(f"{file} has no gtf file")
                                    write_log_file(log_type="subdir_dl", file_name=file)
                                    item_check += 1
                                    ftp.chdir(ftp_dir + item + "/latest_assembly_versions") 
                                    continue
                            except ftputil.error.FTPOSError:
                                    logging.error("FTPOSError occurred for file: %s. Skipping...", file)
                                    time.sleep(5)
                                    continue
                            if genomic_fna_check + genomic_gtf_check == 2:
                                print(f"{file} Files Downloaded")
                                if verify_checksums(local_path_gtf, file + "_genomic.gtf.gz") and verify_checksums(local_path_fna, file + "_genomic.fna.gz"):                            
                                    write_log_file(log_type="subdir_dl", file_name=file)
                                    write_metadata(assembly=file, genbank_name=item, lineage="")
                                    item_check += 1
                                    ftp.chdir(ftp_dir + item + "/latest_assembly_versions")
                                else:
                                    break
                                
            if item_check == len(dir_files):
                write_log_file(log_type="genome", file_name=item)  
                ftp.close()
                break          
        #ftp.chdir(ftp_dir)  
                print("--------------------")  




