#!/usr/bin/env python3

import json
from typing import Dict, List, TextIO
from collections import defaultdict

class MeasurementsPerASN:
    file_d: TextIO
    target_ip: str
    measurements: Dict[str, List]

    def __init__(self, fd, target_ip):
        self.file_d = fd
        self.target_ip = target_ip
        self.measurements = defaultdict(list)

    def compute_measurements(self):
        data = json.load(self.file_d)
        for traceroute in data:
            if traceroute["dst_addr"] == self.target_ip:
                self.measurements[traceroute["src_addr"]].append(traceroute["result"])

    def print_test(self):
        for key, value in self.measurements.items():
            print(key, value)


class ROVEnforcing:
    measurements_anchor: MeasurementsPerASN
    measurements_experiment: MeasurementsPerASN

    def __init__(self,  measurements_anchor, measurements_experiment):
        self.measurements_anchor = measurements_anchor
        self.experiment_ip = measurements_experiment

    def is_rov_enforcing(self, origin_asn) -> bool:
        pass


def main():
    fd = open("measurements.json", "r")

    asn_measurement = MeasurementsPerASN(fd)

    asn_measurement.compute_measurements()
    asn_measurement.print_test()

main()
