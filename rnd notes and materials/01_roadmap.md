# Roadmap

## North Star

Build Smart Grid Lab from prototype to a usable digital twin/research platform for comparable microgrid use cases.

## Current Stage

`Stage 0 - Foundational prototype`

- Dash window for setup and simulation
- UI-selectable forecast H₂ control slice on synthetic data
- Clean layering started (UI -> application -> infrastructure)
- Early architecture and experimentation flow in place

## Strategic Sequence

1. **Admin foundation (done/in progress)**
   - README, notes system, media strategy
2. **Use-case definition**
   - industrial scenario definition (e.g., electrolyser control from forecasts)
3. **Architecture hardening**
   - thin callbacks, richer application use cases, stable setup schema
4. **Simulation capability growth**
   - hydrogen chain components and cross-window demos
5. **Validation and comparability**
   - benchmark scenarios, metric tables, sensitivity runs
6. **Pilot readiness**
   - reproducible reports, scenario packs, communication assets

## Near-Term Priorities (next 2-4 weeks)

- **UC-OFFGRID-H2-FORECAST-CONTROL** — compare oracle vs rolling forecast behavior in UI
- Add explicit curtailment/residual-energy KPIs for forecast H₂ runs
- Implement first end-to-end use case in incremental slices (application → core integration → UI)
- Expand JSON persistence to scenario save/load UX
- Publish at least one technical progress post

## Definition of Done (for each milestone)

- Clear objective and assumptions
- Reproducible run path
- Output figure/table with interpretation
- Notes entry (decision + experiment)
- Communication-ready short summary
