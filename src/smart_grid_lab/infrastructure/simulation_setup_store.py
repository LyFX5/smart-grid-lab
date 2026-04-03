from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd


def _series_to_payload(series: pd.Series) -> Dict[str, List[Any]]:
    """Convert a pandas Series to a JSON-serializable payload."""
    return {
        "index": [str(ts) for ts in series.index],
        "values": [float(v) for v in series.tolist()],
    }


def _series_from_payload(payload: Dict[str, Iterable[Any]]) -> pd.Series:
    """Reconstruct a pandas Series from a payload previously produced here."""
    index = pd.to_datetime(list(payload["index"]))
    values = list(payload["values"])
    return pd.Series(data=values, index=index, dtype=float)


@dataclass
class SimulationSetupDTO:
    """
    JSON-serializable representation of a simulation setup.

    This mirrors the application-layer `SimulationSetup` but replaces Series
    with primitive lists so it can be stored as JSON.
    """

    time: Dict[str, Any]
    battery: Dict[str, Any]
    solar_profile: Dict[str, Any]
    load_profile: Dict[str, Any]


def setup_to_dto(setup: "smart_grid_lab.application.use_cases.run_simulation.SimulationSetup") -> SimulationSetupDTO:  # type: ignore[name-defined]
    """Adapt an application-layer setup to a DTO suitable for JSON storage."""
    return SimulationSetupDTO(
        time=asdict(setup.time),
        battery=asdict(setup.battery),
        solar_profile=_series_to_payload(setup.solar_profile),
        load_profile=_series_to_payload(setup.load_profile),
    )


def dto_to_setup(
    dto: SimulationSetupDTO,
) -> "smart_grid_lab.application.use_cases.run_simulation.SimulationSetup":  # type: ignore[name-defined]
    """Rebuild an application-layer setup from a DTO."""
    from smart_grid_lab.application.use_cases.run_simulation import (  # local import to avoid cycles
        BatteryConfig,
        SimulationSetup,
        TimeConfig,
    )

    time_cfg = TimeConfig(**dto.time)
    battery_cfg = BatteryConfig(**dto.battery)
    solar = _series_from_payload(dto.solar_profile)
    load = _series_from_payload(dto.load_profile)
    return SimulationSetup(time=time_cfg, battery=battery_cfg, solar_profile=solar, load_profile=load)


def save_setup(dto: SimulationSetupDTO, path: str | Path) -> None:
    """Persist a setup DTO to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(asdict(dto), indent=2), encoding="utf-8")
    tmp_path.replace(path)


def load_setup(path: str | Path) -> SimulationSetupDTO:
    """Load a setup DTO from a JSON file."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return SimulationSetupDTO(**data)

