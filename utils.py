import zipfile
import os
import pandas as pd
import shutil


def extract_gtfs(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def filter_gtfs_by_agency(extract_to, agency_id, output_zip):
    # Load necessary GTFS files
    agency = pd.read_csv(os.path.join(extract_to, "agency.txt"), dtype=str)
    routes = pd.read_csv(os.path.join(extract_to, "routes.txt"), dtype=str)
    trips = pd.read_csv(os.path.join(extract_to, "trips.txt"), dtype=str)
    stop_times = pd.read_csv(os.path.join(extract_to, "stop_times.txt"), dtype=str)
    stops = pd.read_csv(os.path.join(extract_to, "stops.txt"), dtype=str)
    shapes = pd.read_csv(os.path.join(extract_to, "shapes.txt"), dtype=str)
    calendar = pd.read_csv(os.path.join(extract_to, "calendar.txt"), dtype=str)
    calendar_dates = pd.read_csv(
        os.path.join(extract_to, "calendar_dates.txt"), dtype=str
    )

    # Step 1: Filter agency.txt
    filtered_agency = agency[agency["agency_id"] == agency_id]
    if filtered_agency.empty:
        print("Dataframe filtered_agency it's empty.")
    else:
        print(f"filtered_agency contains {len(filtered_agency)} rows.")

    # Step 2: Filter routes.txt based on agency_id
    filtered_routes = routes[routes["agency_id"] == agency_id]
    filtered_route_ids = filtered_routes["route_id"].tolist()
    if filtered_routes.empty:
        print("Dataframe filtered_routes it's empty.")
    else:
        print(f"filtered_routes contains {len(filtered_routes)} rows.")

    # Step 3: Filter trips.txt based on filtered routes
    filtered_trips = trips[trips["route_id"].isin(filtered_route_ids)]
    filtered_trip_ids = filtered_trips["trip_id"].tolist()
    filtered_shape_ids = filtered_trips["shape_id"].dropna().unique()
    filtered_routes = routes[routes["agency_id"] == agency_id]
    filtered_route_ids = filtered_routes["route_id"].tolist()
    if filtered_trips.empty:
        print("Dataframe filtered_trips it's empty.")
    else:
        print(f"filtered_trips contains {len(filtered_trips)} rows.")

    # Step 4: Filter stop_times.txt based on filtered trips
    filtered_stop_times = stop_times[stop_times["trip_id"].isin(filtered_trip_ids)]
    filtered_stop_ids = filtered_stop_times["stop_id"].unique()
    filtered_routes = routes[routes["agency_id"] == agency_id]
    filtered_route_ids = filtered_routes["route_id"].tolist()
    if filtered_stop_times.empty:
        print("Dataframe filtered_stop_times it's empty.")
    else:
        print(f"filtered_stop_times contains {len(filtered_stop_times)} rows.")

    # Step 5: Filter stops.txt based on filtered stop_times
    filtered_stops = stops[stops["stop_id"].isin(filtered_stop_ids)]
    if filtered_stops.empty:
        print("Dataframe filtered_stops it's empty.")
    else:
        print(f"filtered_stops contains {len(filtered_stops)} rows.")

    # Step 6: Filter shapes.txt based on filtered shape_ids
    filtered_shapes = shapes[shapes["shape_id"].isin(filtered_shape_ids)]
    if filtered_shapes.empty:
        print("Dataframe filtered_shapes it's empty.")
    else:
        print(f"filtered_shapes contains {len(filtered_shapes)} rows.")

    # Step 7: Filter calendar.txt based on filtered trips
    filtered_calendar = calendar[
        calendar["service_id"].isin(filtered_trips["service_id"])
    ]
    if filtered_calendar.empty:
        print("Dataframe filtered_calendar it's empty.")
    else:
        print(f"filtered_calendar contains {len(filtered_calendar)} rows.")

    # Step 8: Filter calendar_dates.txt based on filtered calendar
    filtered_calendar_dates = calendar_dates[
        calendar_dates["service_id"].isin(filtered_calendar["service_id"])
    ]
    if filtered_calendar_dates.empty:
        print("Dataframe filtered_calendar_dates it's empty.")
    else:
        print(f"filtered_calendar_dates contains {len(filtered_calendar_dates)} rows.")

    # Save filtered data to new CSV files
    os.makedirs("filtered_gtfs", exist_ok=True)
    filtered_agency.to_csv("filtered_gtfs/agency.txt", index=False)
    filtered_routes.to_csv("filtered_gtfs/routes.txt", index=False)
    filtered_trips.to_csv("filtered_gtfs/trips.txt", index=False)
    filtered_stop_times.to_csv("filtered_gtfs/stop_times.txt", index=False)
    filtered_stops.to_csv("filtered_gtfs/stops.txt", index=False)
    filtered_shapes.to_csv("filtered_gtfs/shapes.txt", index=False)
    filtered_calendar.to_csv("filtered_gtfs/calendar.txt", index=False)
    filtered_calendar_dates.to_csv("filtered_gtfs/calendar_dates.txt", index=False)

    # Copy any other files without filtering
    for file_name in os.listdir(extract_to):
        if file_name not in [
            "agency.txt",
            "routes.txt",
            "trips.txt",
            "stop_times.txt",
            "stops.txt",
            "shapes.txt",
            "calendar.txt",
            "calendar_dates.txt",
        ]:
            shutil.copy(os.path.join(extract_to, file_name), "filtered_gtfs")

    # Create new ZIP file with filtered data
    with zipfile.ZipFile(output_zip, "w") as zipf:
        for root, _, files in os.walk("filtered_gtfs"):
            for file in files:
                zipf.write(os.path.join(root, file), file)

    shutil.rmtree("filtered_gtfs")
