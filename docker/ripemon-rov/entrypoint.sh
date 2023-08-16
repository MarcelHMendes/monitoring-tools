#!/usr/bin/dumb-init /bin/bash
set -e

pushd /root/
exec python3 fetch-measurements.py --api-key "$API_KEY" --measurement-ids "/var/monitor/data/ids-file" --start-date "2023-05-11" --stop-date "2023-06-11" --outdir "/var/monitor/data/ripe-measurements/"
