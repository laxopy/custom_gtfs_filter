import zipfile
import os
import shutil
import pandas as pd
from .utils import extract_gtfs, filter_gtfs_by_agency

def filter_gtfs(zip_path, agency_id, output_zip):
    extract_to = 'temp_gtfs'
    extract_gtfs(zip_path, extract_to)
    filter_gtfs_by_agency(extract_to, agency_id, output_zip)
    shutil.rmtree(extract_to)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Filter GTFS by agency ID')
    parser.add_argument('zip_path', type=str, help='Path to the input GTFS zip file')
    parser.add_argument('agency_id', type=str, help='Agency ID to filter by')
    parser.add_argument('output_zip', type=str, help='Path to the output filtered GTFS zip file')

    args = parser.parse_args()
    filter_gtfs(args.zip_path, args.agency_id, args.output_zip)