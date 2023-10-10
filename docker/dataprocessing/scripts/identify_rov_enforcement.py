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

    def _is_between_period(self, measurement_end_time) -> bool:
        """Test if the measument timestamp is between a time period"""
        timestamp_datetime = datetime.fromtimestamp(measurement_end_time)
        if (
            self.start_period
            < timestamp_datetime.time(measurement_end_time)
            < self.end_period
        ):
            return True
        return False

    def compute_measurements(self) -> None:
        """Filter measurement data according to the target_ip and time parameters"""
        data = json.load(self.file_d)
        for traceroute in data:
            if traceroute["dst_addr"] == self.target_ip and self._is_between_period(
                traceroute["end_time"]
            ):
                self.measurements[traceroute["origin_asn"]].append(traceroute["result"])

    def print_test(self):
        for key, value in self.measurements.items():
            print(key, value)


class ROVEnforcing:
    measurements_anchor_valid: MeasurementsPerASN
    measurements_experiment_valid: MeasurementsPerASN

    measurements_anchor_invalid: MeasurementsPerASN
    measurements_experiment_invalid: MeasurementsPerASN

    TARGET_ASN = 47065

    def __init__(
        self, anchor_valid, experiment_valid, anchor_invalid, experiment_invalid
    ):
        self.measurements_anchor_valid = anchor_valid
        self.measurements_experiment_valid = experiment_valid
        self.measurements_anchor_invalid = anchor_invalid
        self.measurements_experiment_invalid = experiment_invalid

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

    def __del_asn_entry(self, asn) -> None:
        del self.measurements_anchor_valid[asn]
        del self.measurements_experiment_valid[asn]
        del self.measurements_anchor_invalid[asn]
        del self.measurements_experiment_invalid[asn]

    def __check_consistency(self, measurements, threshold) -> None:
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
        """Receive potentially rov enforcement list and classify the type of enforcement"""
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

    anchor_valid = MeasurementsPerASN(
        file_d=fd,
        traget_ip="138.185.228.1",
        start_period=datetime.time(0, 0, 0),
        end_period=datetime.time(12, 00, 00),
    )

    anchor_valid.compute_measurements()
    anchor_valid.print_test()


if __name__ == "__main__":
    sys.exit(main())
