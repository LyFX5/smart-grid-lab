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
