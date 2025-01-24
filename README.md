# Purpose
## Methods to work with open street map and open street planner data

### Installation of osmium for conversions
```
add-apt-repository ppa:osmosisdev/osmosis
apt update
apt install osmium-tool -y
osmium --version
```

### Reduce map to only area you want to use
```
osmconvert norway-latest.osm.pbf -b=8.4,58.56,11.4,60.24 --complete-ways -o=oslo.osm.pbf

```

### Merging open street map .pbf files 
```
osmium merge finland-latest.osm.pbf norway.osm.pbf -o norway-helsinki.pbf
```

### Merging gtfs transition files 
```
#apt-get install nodejs zip
#npm install -g gtfsmerge
gtfsmerge helsinki.gtfs.zip oslo.gtfs.zip merged.gtft.zip
```

### Normalizing transition data
Converting areas with different time zones requires normalization to create open streen planner data
Example of usage:
```
from normalize_gtfs_timezones import normalize_gtfs_timezones
normalize_gtfs_timezones('oslo.gtfs.zip', 'oslo.normalized.gtfs.zip', 'Europe/Oslo')
#or just:
normalize_gtfs_timezones('merged.gtfs.zip', 'merged.gtfs.normalized.zip')
```
