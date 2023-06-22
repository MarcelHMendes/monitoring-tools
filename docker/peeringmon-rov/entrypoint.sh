#!/usr/bin/dumb-init /bin/bash
set -e

pushd /root/
exec python3 bgpstream-downloader.py --prefixes "138.185.229.0/24" --dump_type "updates" --project "ripe_ris"
