#!/bin/bash
set -eu


# cleanup before exit
trap 'rm -f ips_file ips_file_sorted ips_mapped ips_mapped_sorted ips_mapped.csv' EXIT

function remove_duplicates_addr () {
    awk -F ',' -v col="2" '
    BEGIN {
        getline;  # Read the header line and print it
        print;
    }
    {
        if (!($col in seen)) {
            seen[$col] = 1;
            print;
        }
    }
'
}

# Create db
python3 db.py

python3 traceroutes_ip2file.py --ripedir "/etc/peering/monitor/data/ripe-measurements" --outdir ips_file

# remove duplicates and sort IPs
sort -u ips_file > ips_file_sorted

# AS lookup
netcat whois.cymru.com 43 < ips_file_sorted | sort -n > ips_mapped

# remove duplicates and sort mapped ips
sort -u ips_mapped > ips_mapped_sorted

# remove spaces, add comma separation and remove duplicate mapping
sed 's/ //g; s/|/,/g'  ips_mapped_sorted  | cut -d',' -f1-3 | remove_duplicates_addr > ips_mapped.csv

# import data to database
sqlite3 cymru.db ".import --csv ips_mapped.csv ip_asn_mapping"


python3 process-ripe-mesurements.py --ripedir /etc/peering/monitor/data/ripe-measurements/ --db_file cymru.db --outdir mesurements_"$(date +%F)".json

python3 identify_rov_enforcement.py
