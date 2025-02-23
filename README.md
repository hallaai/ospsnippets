# Purpose
## Methods to work with open street map and open street planner data

#Need to have one of latest jdk
```sh
wget https://download.oracle.com/java/23/latest/jdk-23_linux-x64_bin.deb
dpkg -i jdk-23_linux-x64_bin.deb
java --version
```

### Installation of osmium for conversions
```sh
add-apt-repository ppa:osmosisdev/osmosis
apt update
apt install osmium-tool -y
osmium --version
```

## Download area data
```sh
wget https://download.geofabrik.de/europe/norway-latest.osm.pbf -O norway.osm.pbf
wget https://storage.googleapis.com/marduk-production/outbound/gtfs/rb_norway-aggregated-gtfs.zip -O norway.gtfs.zip
```

### Reduce map to only area you want to use
```sh
osmconvert norway-latest.osm.pbf -b=8.4,58.56,11.4,60.24 --complete-ways -o=oslo.osm.pbf

```

### Merging open street map .pbf files 
```sh
osmium merge finland-latest.osm.pbf norway.osm.pbf -o norway-helsinki.pbf
```

### Merging gtfs transition files 
```sh
#apt-get install nodejs zip
#npm install -g gtfsmerge
gtfsmerge helsinki.gtfs.zip oslo.gtfs.zip merged.gtft.zip
```

### Normalizing transition data
Converting areas with different time zones requires normalization to create open streen planner data
Example of usage:
```python
from normalize_gtfs_timezones import normalize_gtfs_timezones
normalize_gtfs_timezones('oslo.gtfs.zip', 'oslo.normalized.gtfs.zip', 'Europe/Oslo')
#or just:
normalize_gtfs_timezones('merged.gtfs.zip', 'merged.gtfs.normalized.zip')
```

## Time format
If you have time format warning then you can instruct pandas difectly to 
```python
def normalize_gtfs_timezones(gtfs_file, output_file, target_timezone='UTC'):
    # Load GTFS files
    with ZipFile(gtfs_file, 'r') as zip_ref:
        # Read agency.txt to get the feed's time zone
        agency = pd.read_csv(zip_ref.open('agency.txt'))

        # Read stop_times.txt with explicit dtypes to avoid mixed-type warnings
        stop_times = pd.read_csv(
            zip_ref.open('stop_times.txt'),
            dtype={
                'trip_id': str,
                'arrival_time': str,
                'departure_time': str,
                'stop_id': str,
                'stop_sequence': int,
                'pickup_type': 'Int64',  # Use 'Int64' for nullable integer type
                'drop_off_type': 'Int64',
                'shape_dist_traveled': float
            }
        )

        # Convert GTFS times to valid datetime strings
        stop_times['arrival_time'], arrival_day_offset = zip(*stop_times['arrival_time'].apply(convert_gtfs_time))
        stop_times['departure_time'], departure_day_offset = zip(*stop_times['departure_time'].apply(convert_gtfs_time))

        # Combine time and day offset into a datetime object
        stop_times['arrival_time'] = pd.to_datetime(stop_times['arrival_time'], format='%H:%M:%S') + pd.to_timedelta(arrival_day_offset, unit='d')
        stop_times['departure_time'] = pd.to_datetime(stop_times['departure_time'], format='%H:%M:%S') + pd.to_timedelta(departure_day_offset, unit='d')

        # Convert to the target timezone
        feed_timezone = pytz.timezone(agency['agency_timezone'].iloc[0])
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
```

### Time zone replacement
It is sometimes happen so that in different gtfs files or merged into one there are different time zones are use. To change it into one, use script replce_string_inzip.py
