import logging
import os
import shutil
import zipfile
import pandas as pd
from utils import extract_gtfs, filter_gtfs_dataset, load_route_ids_from_file


def filter_gtfs(zip_path, filter_type, filter_values, output_zip):
    extract_to = "temp_gtfs"
    extract_gtfs(zip_path, extract_to)
    try:
        filter_gtfs_dataset(
            extract_to,
            output_zip,
            filter_type,
            filter_values,
            log=logging.getLogger("gtfs_filter").info,
        )
    finally:
        if os.path.exists(extract_to):
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


def get_route_ids_from_user(zip_path):
    extract_to = "temp_routes_preview"
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extract("routes.txt", extract_to)

        routes_path = os.path.join(extract_to, "routes.txt")
        routes_df = pd.read_csv(routes_path, dtype=str)

        preview_columns = [col for col in ["route_id", "route_short_name", "route_long_name"] if col in routes_df.columns]
        if preview_columns:
            print("Available routes preview:")
            print(routes_df[preview_columns].head().to_string(index=False))
        else:
            print("routes.txt loaded. Provide route_ids using a CSV or routes.txt file.")
    finally:
        shutil.rmtree(extract_to, ignore_errors=True)

    while True:
        route_file = input(
            "Enter the path to a CSV or routes.txt containing the route_ids to filter: "
        ).strip()
        if not route_file:
            print("A route list file is required to filter by route_id.")
            continue

        route_file_path = os.path.abspath(route_file)
        try:
            route_ids = load_route_ids_from_file(route_file_path)
        except (FileNotFoundError, pd.errors.EmptyDataError) as err:
            print(f"Unable to read route list: {err}")
            continue

        if not route_ids:
            print("The provided file does not contain any route_ids. Please try again.")
            continue

        print(f"Loaded {len(route_ids)} unique route_ids from {route_file_path}.")
        return route_ids


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
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
    filter_mode = ""
    while filter_mode not in {"agency", "route"}:
        filter_mode = input("Filter by 'agency' or 'route'? ").strip().lower()

    if filter_mode == "agency":
        agency_id = get_agency_id_from_user(input_zip_path)
        filter_values = [agency_id]
        output_name_fragment = agency_id
    else:
        route_ids = get_route_ids_from_user(input_zip_path)
        filter_values = route_ids
        output_name_fragment = f"routes_{len(route_ids)}"

    output_zip_path = os.path.join(gtfs_out_dir, f"filtered_gtfs_{output_name_fragment}.zip")

    os.makedirs(gtfs_out_dir, exist_ok=True)

    filter_gtfs(input_zip_path, filter_mode, filter_values, output_zip_path)

    print(f"Filtered GTFS has been saved to {output_zip_path}")
