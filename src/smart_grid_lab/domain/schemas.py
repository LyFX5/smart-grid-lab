from pandas import DataFrame


meta = {"name": "test_microgrid", "created_at": "...", "version": "0.1"}


time = {
    "start": "2024-01-01 00:00:00",
    "end": "2024-01-03 00:00:00",
    "step_minutes": 10,
}


components = {
    "solar_1": {"type": "solar", "params": {"capacity_kw": 50}},
    "load_1": {"type": "load", "params": {}},
    "battery_1": {
        "type": "battery",
        "params": {
            "capacity_kwh": 100,
            "max_charge_kw": 30,
            "max_discharge_kw": 30,
            "efficiency": 0.95,
            "initial_soc": 0.5,
        },
    },
}


topology = {
    "connections": [
        {"from": "solar_1", "to": "bus"},
        {"from": "battery_1", "to": "bus"},
        {"from": "bus", "to": "load_1"},
    ]
}


control = {
    "controller": {
        "type": "rule_based",
        "params": {"battery_priority": "self_consumption"},
    }
}


forecasting = {
    "load_1": {"model": "sarimax", "params": {}, "horizon_hours": 6},
    "solar_1": {"model": "naive", "params": {}},
}


simulation = {
    "mode": "deterministic",  # later: stochastic
    "record_internal_states": True,
}


setup = {
    "meta": {...},
    "time": {...},
    "components": {...},
    "topology": {...},
    "control": {...},
    "forecasting": {...},
    "simulation": {...},
}


setup = {
    "time": {...},
    "components": {"load_1": {...}, "solar_1": {...}, "battery_1": {...}},
    "control": {...},
}


result = {"telemetry": DataFrame, "metrics": DataFrame}
