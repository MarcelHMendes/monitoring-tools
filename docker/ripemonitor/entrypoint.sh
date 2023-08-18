#!/usr/bin/dumb-init /bin/bash
set -e

pushd /root/

NUM_DAYS_CONSIDERED=7
START_DATE=$(date --date "$NUM_DAYS_CONSIDERED days ago" +%Y-%m-%d)
STOP_DATE=$(date +%Y-%m-%d)


exec python3 fetch-measurements.py --api-key "$API_KEY" --measurement-ids "/var/monitor/data/ids-file" --start-date "$START_DATE" --stop-date "$STOP_DATE" --outdir "/var/monitor/data/ripe-measurements/"
