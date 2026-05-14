# Use Case: Forecast-Based Hydrogen Production Control (Off-Grid Microgrid)

## Objective

Operate an **off-grid** microgrid with **solar**, **load**, **battery**, **electrolyser**, and **hydrogen storage** so that electrolyser power follows a **forecast-informed** policy, while **all dynamics are stepped through the core simulation engine** (`Microgrid` + `Simulation`).

## Layered architecture (your framework)

| Layer | Responsibility |
|-------|------------------|
| **Core** | Physics and time-stepping for **all microgrid components** (including hydrogen). **Forecast model contracts** (e.g. `SurplusForecastModel`) and **reference heuristics** (oracle, rolling mean). **Control strategies** that consume forecasts and emit `action` dicts for the engine (e.g. `ForecastElectrolyserBatteryStrategy`). |
| **Infrastructure** | **Inference** and external artifacts: load sklearn/onnx models, call APIs, read Parquet, etc. Adapters implement the **same core forecast interface** (e.g. `SklearnSurplusForecastAdapter`). |
| **Application** | **Concrete use cases**: pick `forecast_1` vs `forecast_2`, pick strategy version, wire `SetUp` + injected `strategy`, run `Simulation`. No duplicate time loop outside core. |
| **UI** | Depends only on **application** use cases (thin callbacks). |

Data flow:

```text
UI → application use case → Simulation(strategy, SetUp with H2 components)
         ↑                           ↓
   infrastructure adapter     core Microgrid.step
   (forecast inference)       core components + policy math
```

## Objective function (evolving)

At each step `t`:

1. **Observe** microgrid state (via `Microgrid.state()`).
2. **Forecast** scalar surplus (kW) using a `SurplusForecastModel` (core heuristic or infra adapter).
3. **Decide** electrolyser `pr` and **residual battery** power via `ForecastElectrolyserBatteryStrategy`.
4. **Step** the engine: solar/load timestamps, battery, electrolyser, then **tank mass balance** from electrolyser production (inside `Microgrid`).

## Phases

### Phase A (current)

- H₂ components **integrated in core** `Microgrid` stepping.
- Forecast **contract** in core; oracle / rolling **implementations** in core.
- Application use case: `run_forecast_h2_offgrid_simulation`.

### Phase B

- Richer power balance (curtailment, SOC-aware electrolyser caps, fuel cell).
- Additional strategies in `core/controllers/`.

### Phase C

- Replace heuristics with **infrastructure** trained forecasters under the same interface.
- Scenario persistence includes forecaster id + hyperparameters.

## Code map

- Use case: `src/smart_grid_lab/application/use_cases/off_grid_h2_forecast_control.py`
- Forecast ABC + heuristics: `src/smart_grid_lab/core/forecasting/`
- Policy helper: `src/smart_grid_lab/core/controllers/h2_surplus_policy.py`
- Strategy: `src/smart_grid_lab/core/controllers/forecast_h2_battery_strategy.py`
- Microgrid coupling: `src/smart_grid_lab/core/microgrid.py`
- Infra adapter stub: `src/smart_grid_lab/infrastructure/forecasting/sklearn_surplus_adapter.py`

## KPIs (experiment log)

- Curtailed energy, H₂ mass, tank violations, ramp cycles / degradation proxy.

## Open questions

- Expose `Solar.pv_plant_area` as configuration (today use case assumes 100 m² for kW → irradiance mapping).
- Fuel cell dispatch and grid-forming constraints (Phase B+).
