#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, time
from typing import Dict, List, TextIO


class MeasurementsPerASN:
    data: list
    target_ip: str
    start_time: datetime
    end_time: datetime
    measurements: Dict[str, List]

    def __init__(self, data, target_ip, target_day, start_time, end_time):
        self.data = data
        self.target_ip = target_ip
        self.target_day = target_day
        self.start_time = start_time
        self.end_time = end_time
        self.measurements = defaultdict(list)

    def _is_between_period(self, measurement_end_time) -> bool:
        """Test if the measurement timestamp is in the target day and between a time period"""
        timestamp_datetime = datetime.fromtimestamp(measurement_end_time)
        target_date = datetime.strptime(self.target_day, "%Y-%m-%d")
        if timestamp_datetime.date() != target_date.date():
            return False
        if self.start_time < timestamp_datetime.time() < self.end_time:
            return True
        return False

    def compute_measurements(self) -> None:
        """Filter measurement data according to the target_ip and time parameters"""

        if not self.data:
            logging.error("Error acessing measurements data")
            return
        for traceroute in self.data:
            if (
                traceroute["dst_addr"] == self.target_ip
                and self._is_between_period(traceroute["endtime"])
                and traceroute["origin_asn"] != None
            ):
                self.measurements[
                    (traceroute["origin_asn"], traceroute["src_addr"])
                ].append(traceroute["result"])

    def print_test(self):
        for key, value in self.measurements.items():
            print(key, value)


class ROVEnforcing:
    measurements_anchor_valid: MeasurementsPerASN
    measurements_experiment_valid: MeasurementsPerASN

    measurements_anchor_invalid: MeasurementsPerASN
    measurements_experiment_invalid: MeasurementsPerASN

    peers_asn_list: dict

    TARGET_ASN = 47065

    def __init__(
        self, anchor_valid, experiment_valid, anchor_invalid, experiment_invalid
    ):
        self.measurements_anchor_valid = anchor_valid
        self.measurements_experiment_valid = experiment_valid
        self.measurements_anchor_invalid = anchor_invalid
        self.measurements_experiment_invalid = experiment_invalid
        self.peers_asn_list = defaultdict(tuple)

    # reference: https://github.com/nrodday/TMA-21/blob/main/code/Atlas_rov_identification.py#L802
    # change most_common_trace code to get all traceroutes considered "normal/good"
    def __most_common_trace(self, traceroutes_list) -> (list, float):
        """Returns the most common traceroute and the frequency of ocurrence"""
        total_measurements = len(traceroutes_list)
        trace_counter = Counter(map(tuple, traceroutes_list))
        most_common_trace, count = trace_counter.most_common(1)[0]
        return (most_common_trace, count / total_measurements)

    def __test_peering_reachability(self, trace) -> bool:
        """Test if the traceroute reaches PEERING ASN"""
        first_asn = trace[0]
        if first_asn != self.TARGET_ASN and self.TARGET_ASN in trace:
            return True
        return False

    def __del_asn_entry(self, asn) -> None:
        """Remove asn entry from all measurements"""
        del self.measurements_anchor_valid[asn]
        del self.measurements_experiment_valid[asn]
        del self.measurements_anchor_invalid[asn]
        del self.measurements_experiment_invalid[asn]

    def __check_consistency(self, measurements, threshold) -> None:
        """Get the most common traceroute in list and verify if it is above threshold"""
        for asn in measurements:
            most_common_trace, frequency = self.__most_common_trace(measurements[asn])
            if frequency < threshold or not self.__test_peering_reachability(
                most_common_trace
            ):
                self.__del_asn_entry(asn)

    def check_anchor_consistency(self, threshold) -> None:
        """Check if the frequency of traceroutes in anchor probes is above a threshold"""
        self.__check_consistency(self.measurements_anchor_valid, threshold)
        self.__check_consistency(self.measurements_anchor_invalid, threshold)

    def check_path_compatibility(self) -> None:
        """Check path simmetry when valid ROA (or non-ROA)"""
        for asn in self.measurements_experiment_valid:
            anchor_most_common, _ = self.__most_common_trace(
                self.measurements_anchor_valid[asn]
            )
            experiment_most_common, _ = self.__most_common_trace(
                self.measurements_experiment_valid[asn]
            )

            if anchor_most_common != experiment_most_common:
                self.__del_asn_entry(asn)

    def import_peering_asn_list(self, peer_file):
        fd = open(peer_file, "r")
        data = json.load(fd)
        for connection in data:
            if connection["IP version"] == "IPv4":
                self.peers_asn_list[connection["Session ID"]] = (
                    connection["Peer ASN"],
                    connection["BGP Mux"],
                )

    def potentially_rov_enforcement(self) -> list:
        """Test if there is a difference in paths when invalid ROA (or ROA eq AS0)"""
        asn_include_list = []
        for asn in self.measurements_experiment_invalid:
            anchor_most_common, _ = self.__most_common_trace(
                self.measurements_anchor_invalid[asn]
            )
            experiment_most_common, _ = self.__most_common_trace(
                self.measurements_experiment_invalid[asn]
            )
            if anchor_most_common != experiment_most_common:
                asn_include_list.append(asn)
        return asn_include_list

    def classify_rov_enforcement_type(self, include_list) -> dict:
        """Receive potentially_rov_enforcement list and classify the type of enforcement"""
        classification = {}
        for asn in include_list:
            experiment_most_common = self.__most_common_trace(
                self.measurements_experiment_invalid[asn]
            )
            if self.__test_peering_reachability(experiment_most_common):
                classification[asn] = "route_divergence"
            else:
                classification[asn] = "invalid_fail"
        return classification
        # missing 1_hop/2_plus_hops classification


def create_parser():
    desc = """Identify ASes that enforces ROV"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--target_day",
        dest="target_day",
        action="store",
        required=True,
        help="Chosen day to perform the analysis (e.g 2023-05-19)",
    )
    parser.add_argument(
        "--peers_list",
        dest="peers_list",
        action="store",
        required=True,
        help="PEERING peers list FILE",
    )
    return parser


def main():
    parser = create_parser()
    opts = parser.parse_args()

    filename = f"measurements_{opts.target_day}.json"
    fd = open(os.path.join("/etc/peering/monitor/data/ripe-compiled/", filename), "r")
    data = json.load(fd)

    anchor_valid = MeasurementsPerASN(
        data=data,
        target_ip="138.185.228.1",
        target_day="2023-08-23",
        start_time=time(0, 0, 0),
        end_time=time(12, 00, 00),
    )

    experiment_valid = MeasurementsPerASN(
        data=data,
        target_ip="138.185.229.1",
        target_day="2023-08-23",
        start_time=time(0, 0, 0),
        end_time=time(12, 00, 00),
    )

    experiment_valid.compute_measurements()
    # experiment_valid.print_test()

    anchor_valid.compute_measurements()
    # anchor_valid.print_test()

    rov_identification = ROVEnforcing(
        experiment_valid, experiment_valid, experiment_valid, experiment_valid
    )

    rov_identification.import_peering_asn_list(opts.peers_list)
    rov_identification.print_test_temporary()


if __name__ == "__main__":
    sys.exit(main())
