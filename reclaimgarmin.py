import datetime
import json
import logging
import os
from dotenv import load_dotenv

import requests
from getpass import getpass
from garth.exc import GarthHTTPError

from garminconnect import (
  Garmin,
  GarminConnectAuthenticationError,
  GarminConnectConnectionError,
  GarminConnectTooManyRequestsError
)

# Configure debug logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables if defined
# email = os.getenv("EMAIL")
# password = os.getenv("PASSWORD")
load_dotenv()
email = os.getenv('MAIL')
password = os.getenv('PASSWORD')
api = None
tokenstore = ".garminconnect"

def init_api(email, password):
  try:
    print(
      f"Trying to login to Garmin Connect using token data from '{tokenstore}'...\n"
    )
    garmin = Garmin()
    garmin.login(tokenstore)
  except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
    print(
      "Login tokens not present, login with your Garmin Connect credentials to generate them.\n"
      f"They will be stored in '{tokenstore}' for future use.\n"
    )
    try:
      garmin = Garmin(email, password)
      garmin.login()
      # Save tokens for next login
      garmin.garth.dump(tokenstore)
    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError, requests.exceptions.HTTPError) as err:
      logger.error(err)
      return None
  return garmin


if not api:
  api = init_api(email, password)

def download_json(api_call, filename):
  json_data = json.dumps(api_call, indent=2)
  with open(f"./{filename}", "w") as f:
    f.write(json_data)


# Downloads activities in gpx, tcx, and fit.
# Downloads weather and time in HR zones as json.
def download_activities(startdate, enddate):

  activities = api.get_activities_by_date(startdate, enddate)

  # Download activities
  for activity in activities:

    activity_id = activity["activityId"]
    activity_date = activity["startTimeLocal"][:10]
    filename = os.path.join('data', activity_date, 'activities', str(activity_id), str(activity_id))
    print('Downloading activity from ' + activity_date)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    download_json(activity, filename + '.json')

    download_json(api.get_activity_weather(activity_id), filename + '_weather.json')
    download_json(api.get_activity_hr_in_timezones(activity_id), filename + '_hr-zones.json')
    download_json(api.get_activity_details(activity_id), filename + '_details.json')

    gpx_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.GPX)
    output_file = f"{filename}.gpx"
    with open(output_file, "wb") as fb:
      fb.write(gpx_data)

    tcx_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.TCX)
    output_file = f"{filename}.tcx"
    with open(output_file, "wb") as fb:
      fb.write(tcx_data)

    fit_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)
    output_file = f"{filename}.fit"
    with open(output_file, "wb") as fb:
      fb.write(fit_data)


# Downloads health data like steps, floors, heart rate, ...
def download_health_wellness(start_date, end_date):

  current_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
  end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

# Iterate over the dates from start to end
  while current_date <= end_date:

    filename = os.path.join('data', current_date.strftime("%Y-%m-%d"), 'health')
    os.makedirs(filename, exist_ok=True)
    current_date_str = current_date.strftime("%Y-%m-%d")
    print('Downloading health and wellness data from ' + current_date_str)

    download_json(api.get_stats_and_body(current_date_str), os.path.join(filename, 'summary.json'))
    download_json(api.get_steps_data(current_date_str), os.path.join(filename, 'steps.json'))
    download_json(api.get_heart_rates(current_date_str), os.path.join(filename, 'hr.json')) 
    download_json(api.get_body_battery(current_date_str), os.path.join(filename, 'bodybattery.json'))
    download_json(api.get_floors(current_date_str), os.path.join(filename, 'floors.json'))
    download_json(api.get_rhr_day(current_date_str), os.path.join(filename, 'rhr.json'))
    download_json(api.get_sleep_data(current_date_str), os.path.join(filename, 'sleep.json'))
    download_json(api.get_stress_data(current_date_str), os.path.join(filename, 'stress.json'))
    download_json(api.get_respiration_data(current_date_str), os.path.join(filename, 'respiration.json'))
    download_json(api.get_spo2_data(current_date_str),  os.path.join(filename, 'spo2.json'))
    download_json(api.get_max_metrics(current_date_str), os.path.join(filename, 'maxmetrics.json'))

    current_date += datetime.timedelta(days=1)

while True:
  start_date= input("Start Date (YYYY-MM-DD): ")
  end_date= input("End Date (YYYY-MM-DD): ")

  print('--- Starting activities download ---')
  download_activities(start_date, end_date)
  print('--- Starting health and wellness data download ---')
  download_health_wellness(start_date, end_date)
  break