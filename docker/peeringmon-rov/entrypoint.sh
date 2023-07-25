#!/usr/bin/dumb-init /bin/bash
set -e

pushd /root/
exec python3 bgpstream-downloader.py --prefixes "138.185.229.0/24" --dump_type "updates" --project "ripe_ris" --start-date "2023-07-18" --stop-date "2023-07-23"
#exec python3 fetch-measurements.py --api-key "$API_KEY" --measurement-ids "ids-file" --start-date "2023-05-11" --stop-date "2023-06-11" --outdir "/etc/peering/data/ripe-measurements/"
