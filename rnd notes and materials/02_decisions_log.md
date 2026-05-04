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

### 2026-05-04

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
