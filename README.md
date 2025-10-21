
# GTFS Filter

This project filters GTFS bundles to a subset defined either by `agency_id` or by an explicit list of `route_id`s. The output is a brand new GTFS zip that only contains the relevant rows, plus a console log describing which files were amended and why.

## Installation

1. Clone the repository.
2. Create a virtual environment and install the requirements:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Preparing input data

- Place the GTFS bundle you want to filter inside `GTFS-IN/` (only the first `*.zip` file is processed).
- When filtering by routes you can provide either:
  - A simple CSV with one `route_id` per line (with or without a header).
  - A valid GTFS `routes.txt` file containing the routes you want to keep.

## Running a filter

```bash
python main.py
```

The CLI will prompt you to choose the filter type:

- **agency** – shows the contents of `agency.txt` so you can pick an `agency_id`. The filtered GTFS keeps every file needed for the selected agency.
- **route** – previews the first rows of `routes.txt` and asks for the path to the CSV or `routes.txt` that lists the desired `route_id`s. The tool filters every dependent file (trips, stop_times, stops, shapes, calendars, etc.) to match the chosen routes.

After filtering, a new zip is saved to `GTFS-OUT/` and the console lists each GTFS file that was modified or copied, together with the reason.
