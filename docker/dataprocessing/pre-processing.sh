#!/bin/bash
set -eu

# cleanup before exit
trap 'rm -f ips_file ips_file_sorted ips_mapped ips_mapped_sorted' EXIT

python3 traceroutes_ip2file.py --ripedir "/etc/peering/monitor/data/ripe-measurements" --outdir ips_file

# remove duplicates and sort IPs
sort -u ips_file > ips_file_sorted

netcat whois.cymru.com 43 < ips_file_sorted | sort -n > ips_mapped

# remove duplicates and sort mapped ips
sort -u ips_mapped > ips_mapped_sorted

# remove spaces, add comma separation, add line number in the beggining of the row (We'll use as PK)
sed 's/ //g; s/|/,/g'  ips_mapped_sorted |  nl -w1 -s',' > ips_mapped.csv

# import data to database
sqlite3 my_database.db ".import --csv ips_mapped.csv prefix_asn_mapping"
