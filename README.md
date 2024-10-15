
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

1. Save your Input GTFS in the folder GTFS-IN

2. In order to execute the project, use the following command:

```bash
python main.py
```

3. The application will display all available agency_id in the input GTFS. Type your selection and click INTRO. 

4. The filtered GTFS will be stored at GTFS-OUT. 

