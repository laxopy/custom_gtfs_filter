
# GTFS Filter

This project allows you to filter a GTFS by 'agency_id' and generate a new filtered GTFS containing only that specific agency_id data

## Install it

1. Clone the repository
2. Create a virtual environment and instal the requirements:

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
pip install -r requirements.txt
```

## Run the project

In order to execute the project, use the following command:

```bash
python -m gtfs_filter.main path_to_your_gtfs.zip your_agency_id filtered_gtfs.zip
```

