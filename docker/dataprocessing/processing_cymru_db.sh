#!/bin/bash
set -eu

# cleanup before exit
trap 'rm -f ips_file ips_file_sorted ips_mapped ips_mapped_sorted ips_mapped.csv' EXIT

python3 db.py

python3 traceroutes_ip2file.py --ripedir "/etc/peering/monitor/data/ripe-measurements" --outdir ips_file

# remove duplicates and sort IPs
sort -u ips_file > ips_file_sorted

# ip to as lookup
netcat whois.cymru.com 43 < ips_file_sorted | sort -n > ips_mapped

# remove duplicates and sort mapped ips
sort -u ips_mapped > ips_mapped_sorted

# remove spaces and add comma separation, add line number in the beggining of the row (We'll use as PK),
# remove extra information
sed 's/ //g; s/|/,/g'  ips_mapped_sorted  | cut -d',' -f1-3 > ips_mapped.csv

#|  nl -w1 -s','
# import data to database
sqlite3 cymru.db ".import --csv ips_mapped.csv ip_asn_mapping"