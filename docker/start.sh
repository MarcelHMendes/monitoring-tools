#!/bin/sh
set -eu

path_config=/etc/peering/monitor/config.json
end_date=$(jq -r '.end_date' "$path_config")

# Variable for additional arguments
DOCKER_ARGS=""
USE_BGP=false

echo "Use $0 -h for help"

# Check if there are any arguments passed to the script
while [ "$#" -gt 0 ]; do
    case "$1" in
        -v)
            # Avoid violating a uniqueness constraint
            DOCKER_ARGS="--force-recreate -V"
            shift
            ;;
        -b)
            USE_BGP=true
            shift
            ;;
        -h|--help)
            echo "Use: $0 [-v] [-b]"
            echo "-v force-recreate the dataprocessing volume"
            echo "-b enable BGP monitor"
            exit 0
            ;;
        *)
            echo "Uso: $0 [-v] [-b]"
            exit 1
            ;;
    esac
done

echo "Building containers"
echo docker compose build
docker compose build

echo "Starting container peering_ripemonitor"
echo docker compose up ripemonitor-dump -d
docker compose up ripemonitor-dump -d

# Check if the BGP monitor is enabled
if [ "$USE_BGP" = true ]; then
    echo "Iniciando container peering_bgpmonitor"
    echo docker compose up bgpmonitor-dump -d
    docker compose up bgpmonitor-dump -d
fi

echo "Waiting for peering_ripemonitor to finish..."
while [ "$(docker inspect -f '{{.State.Running}}' peering_ripemonitor)" = "true" ]; do
    sleep 5
done
echo "peering_ripemonitor process ripe-raw_${end_date}"

echo "Starting container peering_dataprocessing"
echo docker compose up $DOCKER_ARGS peeringrov-dataprocessing -d
docker compose up $DOCKER_ARGS peeringrov-dataprocessing -d

echo "Waiting for peering_dataprocessing to finish..."
while [ "$(docker inspect -f '{{.State.Running}}' peering_dataprocessing)" = "true" ]; do
    sleep 10
done
echo "peering_dataprocessing process measurements_${end_date}.json"
