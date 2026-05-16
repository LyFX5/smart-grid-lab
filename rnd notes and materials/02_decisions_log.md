# Decisions Log

Use this file for architecture, modeling, and product decisions.

---

## Template

- `date`:
- `decision`:
- `context`:
- `options_considered`:
- `chosen_option`:
- `rationale`:
- `tradeoffs`:
- `impact_on_next_steps`:

---

## Entries

### 2026-05-14 (revision — layered simulation)

- `decision`: Hydrogen components must step inside **core** `Microgrid` / `Simulation`; application only wires use cases.
- `context`: Align with clean architecture: forecast **definition** in core, **inference** in infrastructure, **composition** in application.
- `options_considered`:
  - keep standalone application time loop for H₂,
  - integrate H₂ in `Microgrid`, inject strategies into `Simulation`.
- `chosen_option`: Extend `Microgrid.step` for ordered dispatch + tank mass balance; add `SurplusForecastModel` + strategies in core; `Simulation(setup, strategy=...)`; application `run_forecast_h2_offgrid_simulation` calls core only.
- `rationale`: Single engine of truth for simulatability and integrability of every component.
- `tradeoffs`: Larger core surface (forecast contracts + strategies) until split into subpackages if needed.
- `impact_on_next_steps`: UI `window2` can call the application use case; wire `SklearnSurplusForecastAdapter` when models exist.

### 2026-05-14 (superseded)

- `note`: Earlier decision to keep Phase A **outside** `Simulation` is superseded by the revision above once hydrogen is first-class in core.

### 2026-05-04 (callbacks vs use case)

- `decision`: Introduce clean layer split for simulation workflow.
- `context`: Callback logic was becoming heavy and mixed orchestration with UI concerns.
- `options_considered`:
  - keep direct core calls in callbacks,
  - move orchestration to application use case.
- `chosen_option`: Move simulation orchestration to `application/use_cases/run_simulation.py`.
- `rationale`: Improves testability and keeps UI callbacks thin.
- `tradeoffs`: Slightly more boilerplate through DTO/config objects.
- `impact_on_next_steps`: Enables adding persistence and use-case variants without callback sprawl.

### 2026-05-04

- `decision`: Add infrastructure adapter for JSON setup storage.
- `context`: Need reproducibility and scenario reuse for experiments and publications.
- `options_considered`:
  - save only UI stores ad-hoc,
  - create dedicated setup DTO + save/load utility.
- `chosen_option`: Create dedicated DTO and adapter in infrastructure.
- `rationale`: Better boundary between application and storage details.
- `tradeoffs`: Requires schema maintenance over time.
- `impact_on_next_steps`: Enables scenario library and comparable runs.

### 2026-05-16 (forecast H₂ UI slice)

- `decision`: Implement the first forecast-based H₂ UI path inside `window1` as a selectable control use case.
- `context`: The next step is incremental UI delivery on synthetic data while preserving the clean layering rule.
- `options_considered`:
  - create a separate dedicated H₂ window immediately,
  - add a mode selector to the existing setup/run/results window.
- `chosen_option`: Add `Battery baseline` vs `Forecast H₂ control` mode selection in `window1`; callbacks stay thin and delegate H₂ execution to `run_forecast_h2_offgrid_from_ui_battery`.
- `rationale`: Fastest usable vertical slice with minimal UI duplication and a clear path to side-by-side comparisons.
- `tradeoffs`: The setup panel is denser; a dedicated scenario page may be needed later.
- `impact_on_next_steps`: Add comparison UX, curtailment KPIs, and infrastructure-backed forecaster selection.
