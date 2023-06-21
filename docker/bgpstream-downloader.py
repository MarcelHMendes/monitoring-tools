#!/usr/bin/env python3
# coding: utf-8

import argparse
import ipaddress
import json
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass
from multiprocessing import Pool
from typing import Annotated, List, Optional, Union

import dateutil
from lib import *


@dataclass
class BGPDump:
    start_time: Annotated[str, "UTC datetime string"]
    end_time: Annotated[str, "UTC datetime string"]
    dump_type: str
    prefixes: List[ipaddress.IPv4Network]
    project: Optional[
        Union[
            Annotated[str, "route_views"],
            Annotated[str, "ripe_ris"],
            Annotated[str, "ris+views"],
        ]
    ] = None
    collectors: Optional[List[str]] = None

    def __post_init__(self):
        self._validate_prefixes()
        self._validate_times()
        self._validate_dump_type()
        self._validate_collectors()

    def _validate_prefixes(self):
        for pfx in self.prefixes:
            prefix = ipaddress.IPv4Network(pfx)

    def _validate_times(self):
        try:
            dateutil.parser.parse(self.start_time)
            dateutil.parser.parse(self.end_time)
        except ValueError:
            sys.exit("Incorrect date values. Must be in UTC datetime string format")

    def _validate_dump_type(self):
        if self.dump_type != "updates" and self.dump_type != "ribs":
            sys.exit("Incorrect record type. Must be 'updates' or 'ribs'")

    def _validate_collectors(self):
        if not self.collectors:
            if self.project == "ripe_ris":
                self.collectors = RIPE_RIS
            elif self.project == "route_views":
                self.collectors = ROUTE_VIEWS
            elif self.project == "ris+views":
                self.collectors = RIPE_RIS + ROUTE_VIEWS

        for collector in self.collectors:
            if collector not in ROUTE_VIEWS and collector not in RIPE_RIS:
                sys.exit("The collector's choice doesn't match any project")

    def download_bgpdump(self):
        stream = download_bgpstream(
            start_time=self.start_time,
            end_time=self.end_time,
            record_type=self.dump_type,
            prefixes=self.prefixes,
            collectors=self.collectors,
        )

        return stream

def process_bgpdump(bgp_dump):
    return bgp_dump.download_bgpdump()

def generate_times_list():

    # Get the current UTC datetime
    current_datetime = datetime.datetime.utcnow()

    # Calculate the start and end datetime for the last week
    start_datetime = current_datetime - timedelta(days=7)
    end_datetime = current_datetime

    # Generate a list of datetime objects for each day in the last week
    date_list = []
    current_date = start_datetime
    while current_date <= end_datetime:
        date_list.append(current_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        current_date += timedelta(days=1)

    return date_list

def create_parser():
    desc = """Download BGPData"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--prefixes",
        nargs="+",
        dest="prefixes",
        action="store",
        required=True,
        help="List of prefixes to be filtered"
    )
    parser.add_argument(
        "--project",
        dest="project",
        type=str,
        action="store",
        default=None,
        required=False,
        help="Name of the project (route_views, ripe_ris, ris+views)"

    )
    parser.add_argument(
        "--dump_type",
        dest="dump_type",
        type=str,
        action="store",
        default=None,
        required=True,
        help="Type of dump (ribs or updates)"
    )
    parser.add_argument(
        "--collectors",
        nargs="+",
        dest="collectors",
        action="store",
        required=False,
        default=None,
        help="Collectors to be used"
    )
    return parser

def main():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)

    parser = create_parser()
    opts = parser.parse_args()

    TIMES = generate_times_list()

    bgp_dumps = []
    for ti in range(0,len(TIMES) - 1):
        bgp_dumps.append(
            BGPDump(
                start_time=TIMES[ti],
                end_time=TIMES[ti + 1],
                dump_type=opts.dump_type,
                prefixes=opts.prefixes,
                project=opts.project,
                collectors=opts.collectors
            )
        )

    pool = Pool()
    results_iterator = list(pool.imap(process_bgpdump, bgp_dumps))

    pool.close()
    pool.join()

    stream_list = []

    for stream in results_iterator:
        stream_list.extend(stream)

    file_name = f"bgpdump_{TIMES[0]}_{TIMES[-1]}_{opts.dump_type}_{opts.project}.json"
    with open(file_name, "w", encoding="utf-8") as fd:
        json.dump(stream_list, fd, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    sys.exit(main())
