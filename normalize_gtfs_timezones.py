# normalize_gtfs_timezones.py
import pandas as pd
import pytz
from zipfile import ZipFile

def convert_gtfs_time(time_str):
    """
    Convert GTFS time (e.g., "26:45:00") to a valid datetime string.
    """
    hours, minutes, seconds = map(int, time_str.split(':'))
    
    # Handle hours >= 24
    day_offset = hours // 24  # Calculate the number of days to add
    hours = hours % 24  # Convert hours to 24-hour format

    # Format the time as HH:MM:SS
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return time_str, day_offset

def normalize_gtfs_timezones(gtfs_file, output_file, target_timezone='UTC'):
    # Load GTFS files
    with ZipFile(gtfs_file, 'r') as zip_ref:
        # Read agency.txt to get the feed's time zone
        agency = pd.read_csv(zip_ref.open('agency.txt'))
        feed_timezone = pytz.timezone(agency['agency_timezone'].iloc[0])

        # Read stop_times.txt
        stop_times = pd.read_csv(zip_ref.open('stop_times.txt'))

        # Convert GTFS times to valid datetime strings
        stop_times['arrival_time'], arrival_day_offset = zip(*stop_times['arrival_time'].apply(convert_gtfs_time))
        stop_times['departure_time'], departure_day_offset = zip(*stop_times['departure_time'].apply(convert_gtfs_time))

        # Combine time and day offset into a datetime object
        stop_times['arrival_time'] = pd.to_datetime(stop_times['arrival_time'], format='%H:%M:%S') + pd.to_timedelta(arrival_day_offset, unit='d')
        stop_times['departure_time'] = pd.to_datetime(stop_times['departure_time'], format='%H:%M:%S') + pd.to_timedelta(departure_day_offset, unit='d')

        # Convert to the target timezone
        stop_times['arrival_time'] = stop_times['arrival_time'].dt.tz_localize(feed_timezone).dt.tz_convert(target_timezone)
        stop_times['departure_time'] = stop_times['departure_time'].dt.tz_localize(feed_timezone).dt.tz_convert(target_timezone)

        # Format as HH:MM:SS
        stop_times['arrival_time'] = stop_times['arrival_time'].dt.strftime('%H:%M:%S')
        stop_times['departure_time'] = stop_times['departure_time'].dt.strftime('%H:%M:%S')

        # Save the normalized GTFS feed
        with ZipFile(output_file, 'w') as output_zip:
            for file in zip_ref.namelist():
                if file == 'stop_times.txt':
                    output_zip.writestr(file, stop_times.to_csv(index=False))
                else:
                    output_zip.writestr(file, zip_ref.read(file))

# Example usage
normalize_gtfs_timezones('merged.gtfs.zip', 'merged.gtfs.normalized.zip')
#normalize_gtfs_timezones('helsinki.gtfs.zip', 'helsinki.gtfs.normalized.zip')
#normalize_gtfs_timezones('oslo.gtfs.zip', 'oslo.gtfs.normalized.zip')