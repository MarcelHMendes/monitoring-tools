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

python3 db.py

python3 traceroutes_ip2file.py --ripedir "/home/mmendes/monitor/data/ripe-measurements" --outdir ips_file

# remove duplicates and sort IPs
sort -u ips_file > ips_file_sorted

# ip to as lookup
netcat whois.cymru.com 43 < ips_file_sorted | sort -n > ips_mapped

# remove duplicates and sort mapped ips
sort -u ips_mapped > ips_mapped_sorted

# remove spaces and add comma separation, remove duplicate mapping
sed 's/ //g; s/|/,/g'  ips_mapped_sorted  | cut -d',' -f1-3 | remove_duplicates_addr > ips_mapped.csv

# import data to database
sqlite3 cymru.db ".import --csv ips_mapped.csv ip_asn_mapping"
