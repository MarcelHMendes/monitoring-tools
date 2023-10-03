#!/usr/bin/env python3
import json
from typing import Dict, List, TextIO
from collections import defaultdict

class MeasurementsPerASN:
    file_d: TextIO
    measurements: Dict[str, List]

    def __init__(self, fd):
        self.file_d = fd
        self.measurements = defaultdict(list)

    def compute_measurements(self):
        data = json.load(self.file_d)
        for traceroute in data:
            self.measurements[traceroute["src_addr"]].append(traceroute["result"])

    def is_rov_enforcing(self, src_address):
        #evaluate
        pass

    def print_test(self):
        for key, value in self.measurements.items():
            print(key, value)

#test

def main():
    fd = open("measurements.json", "r")

    asn_measurement = MeasurementsPerASN(fd)

    asn_measurement.compute_measurements()
    asn_measurement.print_test()

main()
