#!/bin/sh
set -eu

path=/etc/peering/monitor/config.json
end_date=$(jq -r '.end_date' "$path")

# Variable for additional arguments
DOCKER_ARGS=""

# Check if the -v argument was passed to renew the dataprocessing volume
# to avoid violating a uniqueness constraint
if [ "$#" -gt 0 ] && [ "$1" = "-v" ]; then
    DOCKER_ARGS="--force-recreate -V"
fi

echo "Building containers"
echo docker compose build
docker compose build

echo "Starting container peering_ripemonitor"
echo docker compose up ripemonitor-dump -d
docker compose up ripemonitor-dump -d

# echo "Starting container peering_bgpmonitor"
# echo docker compose up bgpmonitor-dump -d
# docker compose up bgpmonitor-dump -d

echo "Waiting for peering_ripemonitor to finish..."
while [ "$(docker inspect -f '{{.State.Running}}' peering_ripemonitor)" = "true" ]; do
    sleep 5
done
echo "peering_ripemonitor process ripe-raw_${end_date}"
sleep 5

echo "Starting container peering_dataprocessing"
echo docker compose up $DOCKER_ARGS peeringrov-dataprocessing -d
docker compose up $DOCKER_ARGS peeringrov-dataprocessing -d

echo "Waiting for peering_dataprocessing to finish..."
while [ "$(docker inspect -f '{{.State.Running}}' peering_dataprocessing)" = "true" ]; do
    sleep 10
done
echo "peering_dataprocessing process measurements_${end_date}.json"
