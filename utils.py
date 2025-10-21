import logging
import os
import shutil
import zipfile
from typing import Callable, List, Optional, Sequence

import pandas as pd


LOGGER = logging.getLogger("gtfs_filter")


REQUIRED_TABLES = (
    "agency.txt",
    "routes.txt",
    "trips.txt",
    "stop_times.txt",
    "stops.txt",
)

OPTIONAL_TABLES = (
    "shapes.txt",
    "calendar.txt",
    "calendar_dates.txt",
)


def extract_gtfs(zip_path: str, extract_to: str) -> None:
    """Extract the provided GTFS zip into a temporary directory."""

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def _read_table(extract_to: str, filename: str) -> pd.DataFrame:
    path = os.path.join(extract_to, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{filename} was not found in the GTFS bundle.")
    return pd.read_csv(path, dtype=str)


def _read_optional_table(extract_to: str, filename: str) -> Optional[pd.DataFrame]:
    path = os.path.join(extract_to, filename)
    if not os.path.exists(path):
        LOGGER.debug("Skipping optional table %s (not present).", filename)
        return None
    return pd.read_csv(path, dtype=str)


def _log_change(log, file_name: str, message: str) -> None:
    log(f"{file_name}: {message}")


def _column_or_first(df: pd.DataFrame, column_name: str) -> pd.Series:
    columns = {col.strip().lower(): col for col in df.columns}
    if column_name in columns:
        return df[columns[column_name]]
    return df.iloc[:, 0]


def load_route_ids_from_file(path: str) -> List[str]:
    """Parse a csv/routes.txt file and return a list of unique route_ids."""

    if not os.path.exists(path):
        raise FileNotFoundError(f"Route filter file not found: {path}")

    try:
        dataframe = pd.read_csv(path, dtype=str)
    except pd.errors.EmptyDataError:
        return []

    series = pd.Series(dtype=str)
    if not dataframe.empty:
        candidate = _column_or_first(dataframe, "route_id")
        cleaned = candidate.dropna().astype(str).str.strip()
        cleaned = cleaned[cleaned.astype(bool)]
        if not cleaned.empty:
            series = cleaned

    if series.empty:
        try:
            dataframe = pd.read_csv(path, dtype=str, header=None)
        except pd.errors.EmptyDataError:
            return []
        if not dataframe.empty:
            candidate = dataframe.iloc[:, 0]
            cleaned = candidate.dropna().astype(str).str.strip()
            cleaned = cleaned[cleaned.astype(bool)]
            series = cleaned

    route_ids = sorted(set(series.tolist()))
    return route_ids


def filter_gtfs_dataset(
    extract_to: str,
    output_zip: str,
    filter_type: str,
    filter_values: Sequence[str],
    log: Optional[Callable[[str], None]] = None,
) -> None:
    """Filter a GTFS dataset keeping only the selected agency or routes."""

    log = log or LOGGER.info

    tables = {name: _read_table(extract_to, name) for name in REQUIRED_TABLES}
    for name in OPTIONAL_TABLES:
        optional = _read_optional_table(extract_to, name)
        if optional is not None:
            tables[name] = optional

    if filter_type == "agency":
        agency_id = filter_values[0]
        filtered_agency = tables["agency.txt"][
            tables["agency.txt"]["agency_id"] == agency_id
        ]
        if filtered_agency.empty:
            raise ValueError(f"No agency entries match agency_id '{agency_id}'.")
        filtered_routes = tables["routes.txt"][
            tables["routes.txt"]["agency_id"] == agency_id
        ]
        descriptor = f"agency_id == '{agency_id}'"
        missing_routes: set[str] = set()
    elif filter_type == "route":
        requested_routes = {value for value in filter_values if value}
        if not requested_routes:
            raise ValueError("No route_ids were provided for filtering.")
        filtered_routes = tables["routes.txt"][
            tables["routes.txt"]["route_id"].isin(requested_routes)
        ]
        if filtered_routes.empty:
            raise ValueError("None of the requested route_ids were found in routes.txt.")
        filtered_agency = tables["agency.txt"][
            tables["agency.txt"]["agency_id"].isin(filtered_routes["agency_id"].dropna().unique())
        ]
        descriptor = f"route_id in {sorted(requested_routes)}"
        present_routes = set(filtered_routes["route_id"].dropna())
        missing_routes = requested_routes.difference(present_routes)
    else:
        raise ValueError("filter_type must be 'agency' or 'route'.")

    filtered_route_ids = filtered_routes["route_id"].dropna().unique()
    trips = tables["trips.txt"]
    filtered_trips = trips[trips["route_id"].isin(filtered_route_ids)]
    if filtered_trips.empty:
        raise ValueError("Filtering removed all trips. Nothing to export.")

    filtered_trip_ids = filtered_trips["trip_id"].dropna().unique()
    stop_times = tables["stop_times.txt"]
    filtered_stop_times = stop_times[stop_times["trip_id"].isin(filtered_trip_ids)]
    filtered_stop_ids = filtered_stop_times["stop_id"].dropna().unique()

    stops = tables["stops.txt"]
    filtered_stops = stops[stops["stop_id"].isin(filtered_stop_ids)]

    filtered_data = {
        "agency.txt": filtered_agency,
        "routes.txt": filtered_routes,
        "trips.txt": filtered_trips,
        "stop_times.txt": filtered_stop_times,
        "stops.txt": filtered_stops,
    }

    if "shapes.txt" in tables:
        shape_ids = filtered_trips["shape_id"].dropna().unique()
        filtered_shapes = tables["shapes.txt"][tables["shapes.txt"]["shape_id"].isin(shape_ids)]
        filtered_data["shapes.txt"] = filtered_shapes
    if "calendar.txt" in tables:
        service_ids = filtered_trips["service_id"].dropna().unique()
        filtered_calendar = tables["calendar.txt"][
            tables["calendar.txt"]["service_id"].isin(service_ids)
        ]
        filtered_data["calendar.txt"] = filtered_calendar
    if "calendar_dates.txt" in tables:
        service_ids = filtered_trips["service_id"].dropna().unique()
        filtered_calendar_dates = tables["calendar_dates.txt"][
            tables["calendar_dates.txt"]["service_id"].isin(service_ids)
        ]
        filtered_data["calendar_dates.txt"] = filtered_calendar_dates

    os.makedirs("filtered_gtfs", exist_ok=True)

    _log_change(log, "agency.txt", f"Kept {len(filtered_agency)} rows ({descriptor}).")
    if filter_type == "route" and missing_routes:
        _log_change(
            log,
            "routes.txt",
            "Missing route_ids: " + ", ".join(sorted(missing_routes)),
        )
    _log_change(
        log,
        "routes.txt",
        f"Kept {len(filtered_routes)} of {len(tables['routes.txt'])} routes ({descriptor}).",
    )
    _log_change(
        log,
        "trips.txt",
        f"Kept {len(filtered_trips)} of {len(trips)} trips for {len(filtered_route_ids)} routes.",
    )
    _log_change(
        log,
        "stop_times.txt",
        f"Kept {len(filtered_stop_times)} of {len(stop_times)} records matching filtered trips.",
    )
    _log_change(
        log,
        "stops.txt",
        f"Kept {len(filtered_stops)} of {len(stops)} stops referenced by remaining stop_times.",
    )

    if "shapes.txt" in filtered_data:
        _log_change(
            log,
            "shapes.txt",
            f"Kept {len(filtered_data['shapes.txt'])} of {len(tables['shapes.txt'])} shapes referenced by filtered trips.",
        )
    if "calendar.txt" in filtered_data:
        _log_change(
            log,
            "calendar.txt",
            f"Kept {len(filtered_data['calendar.txt'])} of {len(tables['calendar.txt'])} services used by filtered trips.",
        )
    if "calendar_dates.txt" in filtered_data:
        _log_change(
            log,
            "calendar_dates.txt",
            f"Kept {len(filtered_data['calendar_dates.txt'])} of {len(tables['calendar_dates.txt'])} service exceptions matching filtered services.",
        )

    for filename, dataframe in filtered_data.items():
        dataframe.to_csv(os.path.join("filtered_gtfs", filename), index=False)

    for file_name in os.listdir(extract_to):
        if file_name in filtered_data:
            continue
        shutil.copy(os.path.join(extract_to, file_name), "filtered_gtfs")
        _log_change(log, file_name, "Copied without modification.")

    with zipfile.ZipFile(output_zip, "w") as zipf:
        for root, _, files in os.walk("filtered_gtfs"):
            for file in files:
                zipf.write(os.path.join(root, file), file)

    shutil.rmtree("filtered_gtfs")
