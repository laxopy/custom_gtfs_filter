import zipfile
import os
import shutil
import pandas as pd
from utils import extract_gtfs, filter_gtfs_by_agency


def filter_gtfs(zip_path, agency_id, output_zip):
    extract_to = "temp_gtfs"
    extract_gtfs(zip_path, extract_to)
    filter_gtfs_by_agency(extract_to, agency_id, output_zip)
    shutil.rmtree(extract_to)


def get_agency_id_from_user(zip_path):
    extract_to = "temp_agency"
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extract("agency.txt", extract_to)

    agency_path = os.path.join(extract_to, "agency.txt")
    agency_df = pd.read_csv(agency_path)

    # Show the first two columns in agency.txt
    print(agency_df.iloc[:, :2].to_string(index=False))

    agency_id = input("Please enter the agency_id to filter: ")

    # Delete temporary folder after using it
    shutil.rmtree(extract_to)

    return agency_id


if __name__ == "__main__":
    gtfs_in_dir = "GTFS-IN/"
    gtfs_out_dir = "GTFS-OUT/"

    # Search the first .zip file in GTFS-IN
    input_zip_files = [f for f in os.listdir(gtfs_in_dir) if f.endswith(".zip")]
    if not input_zip_files:
        print(
            f"No .zip file found in {gtfs_in_dir}. Please place a GTFS .zip file there."
        )
        exit(1)

    input_zip_path = os.path.join(gtfs_in_dir, input_zip_files[0])
    agency_id = get_agency_id_from_user(input_zip_path)

    # Create the output file name
    output_zip_path = os.path.join(gtfs_out_dir, f"filtered_gtfs_{agency_id}.zip")

    # Make sure GTFS-OUT folder exists or else create it
    os.makedirs(gtfs_out_dir, exist_ok=True)

    filter_gtfs(input_zip_path, agency_id, output_zip_path)

    print(f"Filtered GTFS has been saved to {output_zip_path}")
