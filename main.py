import logging
import logging.handlers
import requests
import json
import csv
import os
import pytz
from datetime import date, timedelta, datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

try:
    SOME_SECRET = os.environ["SOME_SECRET"]
except KeyError:
    SOME_SECRET = "Token not available!"
    #logger.info("Token not available!")
    #raise


if __name__ == "__main__":
    # logger.info(f"Token value: {SOME_SECRET}")    
    # Default extracted_date to yesterday (in local time, GMT+7)
    extracted_date = date.today() - timedelta(days=1)

    #Uncomment the following line to choose a custom date manually
    # extracted_date = date(2024, 10, 4)  # Example: Custom date (YYYY, MM, DD)

    date_difference = (date.today() - extracted_date).days + 1

    # Specify the folder where files are saved
    folder_path = 'EC'

    # Generate a dynamic filename by the current day
    csv_filename = os.path.join(folder_path, f'{extracted_date.strftime("%Y-%m-%d")}.csv')

    url = f"https://api.thingspeak.com/channels/2652379/feeds.json?results={2880 * date_difference}" # change this to other numbers if want to get more or less value, approximately 1440 measurements a day

    stored_do_values = []
    csv_data = [['Timestamp (GMT+7)', 'DO Value', 'DO Temperature', 'EC Value (us/cm)', 'EC Temperature', 'Battery Voltage']]  # CSV header

    response = requests.get(url)
    data = json.loads(response.text)

    # Timezones: UTC (GMT+0) and target timezone (GMT+7)
    utc_tz = pytz.timezone('UTC')
    gmt_plus_7_tz = pytz.timezone('Asia/Bangkok')  # GMT+7

    for feed in data['feeds']:
        timestamp = feed.get('created_at', '')

        if timestamp:
            # Parse the timestamp in UTC (GMT+0)
            utc_time = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=utc_tz)

            # Convert the UTC time to GMT+7
            gmt_plus_7_time = utc_time.astimezone(gmt_plus_7_tz)

            # Get the date in GMT+7
            gmt_plus_7_date = gmt_plus_7_time.date()

            # Only append if the date in GMT+7 matches the extracted_date
            if gmt_plus_7_date == extracted_date:
                csv_data.append([
                    gmt_plus_7_time,         # Timestamp in GMT
                    feed.get('field1', ''),  # DO value
                    feed.get('field2', ''),  # DO temperature
                    feed.get('field3', ''),  # EC value (us/cm)
                    feed.get('field4', ''),  # EC temperature
                    feed.get('field5', '')   # Battery Voltage
                ])

    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)

    print(f'Data successfully saved to {csv_filename}')
    logger.info(f'Data successfully saved to {csv_filename}')