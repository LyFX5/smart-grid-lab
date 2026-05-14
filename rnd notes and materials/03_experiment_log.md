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
