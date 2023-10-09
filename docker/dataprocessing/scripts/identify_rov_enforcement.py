#!/usr/bin/env python3

import argparse
from datetime import datetime
import json
import sys
from collections import Counter, defaultdict
from typing import Dict, List, TextIO


class MeasurementsPerASN:
    file_d: TextIO
    target_ip: str
    start_period: datetime
    end_period: datetime
    measurements: Dict[str, List]

    def __init__(self, fd, target_ip, start_period, end_period):
        self.file_d = fd
        self.target_ip = target_ip
        self.start_period = start_period
        self.end_period = end_period
        self.measurements = defaultdict(list)

    def compute_measurements(self):
        data = json.load(self.file_d)
        for traceroute in data:
            if traceroute["dst_addr"] == self.target_ip:  # add time constraint
                self.measurements[traceroute["origin_asn"]].append(traceroute["result"])

    def print_test(self):
        for key, value in self.measurements.items():
            print(key, value)


class ROVEnforcing:
    measurements_anchor: MeasurementsPerASN
    measurements_experiment: MeasurementsPerASN

    # change to measurements_anchor/experiment valid/invalid
    TARGET_ASN = 47065

    def __init__(self, measurements_anchor, measurements_experiment):
        self.measurements_anchor = measurements_anchor
        self.experiment_ip = measurements_experiment

    # reference: https://github.com/nrodday/TMA-21/blob/main/code/Atlas_rov_identification.py#L802
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

    def check_anchor_consistency(self, threshold):
        """Check if the frequency of traceroutes in anchor probes is above a threshold"""
        for asn in self.measurements_anchor:
            most_common_trace, frequency = self.__most_common_trace(
                self.measurements_anchor[asn]
            )
            if frequency < threshold or not self.__test_peering_reachability(
                most_common_trace
            ):
                del self.measurements_anchor[asn]
                del self.measurements_experiment[asn]

    def check_path_compatibility(self):
        """Check path simmetry when valid ROA (or non-ROA)"""
        for asn in self.measurements_experiment:
            anchor_most_common, _ = self.__most_common_trace(
                self.measurements_experiment[asn]
            )
            experiment_most_common, _ = self.__most_common_trace(
                self.measurements_anchor[asn]
            )

            if anchor_most_common != experiment_most_common:
                del self.measurements_anchor[asn]
                del self.measurements_experiment[asn]

    def potentially_rov_enforcement(self) -> list:
        """Test if there is a difference in paths when invalid ROA (or ROA eq AS0)"""
        asn_include_list = []
        for asn in self.measurements_experiment:
            anchor_most_common, _ = self.__most_common_trace(
                self.measurements_experiment[asn]
            )
            experiment_most_common, _ = self.__most_common_trace(
                self.measurements_anchor[asn]
            )
            if anchor_most_common != experiment_most_common:
                asn_include_list.append(asn)
        return asn_include_list

    def classify_rov_enforcement_type(self, include_list) -> dict:
        """Receive potentially rov enforcement list and classify the type of enforcement"""
        classification = {}
        for asn in include_list:
            experiment_most_common = self.__most_common_trace(
                self.measurements_experiment[asn]
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
        "--measurements_file",
        dest="measurements_file",
        action="store",
        required=True,
        help="File where ripe measurements are stored",
    )
    return parser


def main():
    parser = create_parser()
    opts = parser.parse_args()

    fd = open(opts.measurements_file, "r")

    asn_measurement = MeasurementsPerASN(fd, "138.185.228.1")

    asn_measurement.compute_measurements()
    asn_measurement.print_test()


if __name__ == "__main__":
    sys.exit(main())