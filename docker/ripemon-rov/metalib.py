from __future__ import annotations

import dataclasses
import json
import pathlib


@dataclasses.dataclass
class MeasurementInfo:
    measurement_id: int
    target: str
    description: str
    probe_ids: list[int]

    @staticmethod
    def load_from_file(filename: pathlib.Path) -> list[MeasurementInfo]:
        with open(filename) as fd:
            return list(MeasurementInfo(**m) for m in json.load(fd))
