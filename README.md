# ReclaimGarmin

A small python script which uses [python-garminconnect](https://github.com/cyberjunky/python-garminconnect) by cyberjunky to download garmin connect activities and health data.

Downloads activities (GPX, TCX and FIT) and health and wellness data (json).

### Usage

- create a virtual environment `python -m venv venv` and activate it `source venv/bin/activate`
- install requirements `pip install -r requirements.txt`
- set garmin connect password and mail in `.env` file (use `.env.example` as a template)
- run the script `python ./reclaimgarmin.py` and enter start and end date

Data is stored in the data folder grouped by day.
