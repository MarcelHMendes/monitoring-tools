#!/usr/bin/dumb-init /bin/bash
set -e

pushd /root/

start_date=$(jq -r '.start_date' config.json)
end_date=$(jq -r '.end_date' config.json)
api_key=$(jq -r '.api_key' config.json)

exec python3 fetch-measurements.py --api-key "$api_key" --measurement-ids "/var/monitor/data/ids-file" --start-date "$start_date" --stop-date "$end_date" --outdir "/var/monitor/data/ripe-raw_$start_date#$end_date/"
