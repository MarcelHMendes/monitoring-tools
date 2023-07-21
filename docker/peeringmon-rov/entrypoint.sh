#!/usr/bin/dumb-init /bin/bash
set -e

pushd /root/
exec python3 bgpstream-downloader.py --prefixes "138.185.229.0/24" --dump_type "updates" --project "ripe_ris" --start-date "2023-07-19" --stop-date "2023-07-21"
exec python3 fetch-measurements.py --api-key "67970e02-906d-4dd7-a0f9-4e39785b5571" --measurement-ids "ids-file" --start-date "2023-05-11" --stop-date "2023-06-11" --outdir "/etc/peering/data/ripe-measurements/"
