#!/bin/bash
set -eu
#trap remove intermediate files

python3 traceroutes_ip2file.py --ripedir "/etc/peering/monitor/data/ripe-measurements" --outdir ips_file

# remove duplicates and sort IPs
sort -u ips_file > ips_file_sorted

netcat whois.cymru.com 43 < ips_file_sorted | sort -n > ips_mapped

# remove duplicates and sort mapping
sort -u ips_mapped > ips_mapped_sorted

sed 's/ //g; s/|/,/g'  ips_mapped_sorted > ips_mapped.csv
# import data to database
#sqlite3 my_database.db ".import --csv $output_file prefix_asn_mapping"
