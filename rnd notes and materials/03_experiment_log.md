# Experiment Log

This file tracks reproducible experiments and what was learned.

---

## Template

- `experiment_id`:
- `date`:
- `objective`:
- `setup_reference`:
- `assumptions`:
- `method`:
- `key_outputs`:
- `result_summary`:
- `validation_checks`:
- `confidence`:
- `next_action`:

---

## Entries

### EXP-2026-05-14-01

- `date`: 2026-05-14
- `objective`: Validate forecast-informed H₂ use case on the **core** `Simulation` engine.
- `setup_reference`: `run_forecast_h2_offgrid_simulation` + default `OffGridH2ForecastConfig`.
- `assumptions`:
  - solar input as effective kW, mapped to irradiance via default PV area 100 m²,
  - oracle surplus forecast for debugging,
  - battery receives residual after electrolyser schedule.
- `method`: run short horizon; inspect trajectory columns and tank level bounds.
- `key_outputs`: `Results.trajectory` from `Simulation.run`.
- `result_summary`: (run locally when pandas/tqdm available) — code path compiles.
- `validation_checks`: tank level in [0, 1]; no `Microgrid` step exceptions.
- `confidence`: medium pending local run.
- `next_action`: UI window2 + optional `SklearnSurplusForecastAdapter` wiring.

### EXP-2026-05-04-01

- `date`: 2026-05-04
- `objective`: Validate baseline microgrid simulation flow in Dash.
- `setup_reference`: `window1` baseline with sample solar/load + battery defaults.
- `assumptions`:
  - fixed time-step simulation,
  - synthetic solar/load profiles,
  - simple strategy from current core.
- `method`:
  - load sample profiles,
  - run simulation,
  - inspect trajectory figure for expected dynamics.
- `key_outputs`:
  - power traces and battery SOC over time.
- `result_summary`: End-to-end flow operational; UI setup and simulation pipeline connected.
- `validation_checks`:
  - no callback/lint errors,
  - figure renders expected columns.
- `confidence`: medium
- `next_action`: add metrics table and scenario persistence UX.

### EXP-2026-05-16-01

- `date`: 2026-05-16
- `objective`: Validate the forecast H₂ use case with the same synthetic profiles used by the Dash UI.
- `setup_reference`: `window1` synthetic profile defaults + `OffGridH2ForecastConfig` defaults.
- `assumptions`:
  - synthetic irradiance is converted to solar kW using current PV area assumption (100 m²),
  - oracle forecast is the default debugging benchmark,
  - electrolyser current default is conservative (`4 A`) to avoid tank overflow in the multi-day demo.
- `method`: run a 5-day synthetic scenario through `run_forecast_h2_offgrid_from_ui_battery` and inspect scalar KPIs.
- `key_outputs`: energy totals, H₂ produced, final tank level, final battery SOC, electrolyser degradation proxy.
- `result_summary`: Default synthetic run completed with final tank level at the 0.95 policy ceiling and UI-ready metrics generated.
- `validation_checks`: no core simulation exceptions; tank level remains within bounds; trajectory includes H₂ telemetry columns.
- `confidence`: medium for UI/demo behavior; low for physical validation until electrolyser/tank calibration is improved.
- `next_action`: compare oracle and rolling forecast runs and add explicit curtailment/residual-energy KPIs.
