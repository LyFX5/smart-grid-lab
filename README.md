# Smart Grid Lab

Smart Grid Lab is an interactive microgrid laboratory built in Python.  
It is designed to scale step-by-step:

1. `stand` (educational/demo use),
2. `digital twin` (engineering experimentation),
3. `research platform` (comparable scenarios and control studies).

The current focus is a Dash-based UI with clean layering:
`UI callbacks -> application use cases -> core simulation`, plus infrastructure for setup serialization.

## Project Vision

The goal is to help engineers and researchers:
- configure microgrid scenarios quickly,
- run reproducible simulations,
- compare control behavior across use cases,
- communicate results clearly to technical and non-technical stakeholders.

## Current Capabilities

- Interactive Dash window for microgrid setup (`window1`)
- Time horizon setup (start, end, step minutes)
- Sample profile loading for solar irradiance and load power
- Battery initialization parameters
- Simulation run with trajectory visualization
- UI-selectable forecast-based H₂ control use case on synthetic data
- H₂ telemetry visualization for electrolyser power and tank level
- Application-layer `run_simulation` and `run_forecast_h2_offgrid_simulation` use cases
- Infrastructure utilities for JSON serialization of simulation setups

## Architecture (Current Direction)

- `core`: simulation engine and component dynamics (battery, solar, load, microgrid)
- `application`: orchestration use cases (run simulation from high-level setup DTO)
- `infrastructure`: persistence and adapters (JSON setup storage)
- `ui_dash`: presentation layer (layouts, callbacks, graphs)

- `core`: simulation engine, **all microgrid components** (including hydrogen), **forecast model contracts** + reference heuristics, **control strategies** that drive `Simulation` via injected `strategy`.
- `application`: concrete use cases that **compose** core + infrastructure (e.g. `forecast_1` / `forecast_2`, strategy version) and call **`Simulation`**.
- `infrastructure`: **forecast inference** adapters (trained models, APIs), persistence (JSON setups), and other I/O.
- `ui_dash`: presentation only; depends on application use cases.

Principle: **UI → application → Simulation(core) → Microgrid(components)**; infrastructure plugs in at the application wiring boundary.


## Repository Layout

`src/smart_grid_lab/`
- `core/` - domain mechanics and simulation runtime
- `application/use_cases/` - use-case entry points
- `infrastructure/` - storage and serialization adapters
- `ui_dash/` - Dash app, layouts, callbacks
- `domain/` - schemas/builders/validators (evolving)

`rnd notes and materials/`
- structured research/progress notes
- decisions, experiments, roadmap, and communication assets

## Getting Started

### 1) Create environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[ui]"
```

If `.[ui]` extras are unavailable in your environment, install manually:

```bash
python3 -m pip install dash plotly pandas numpy scipy tqdm
python3 -m pip install -e .
```

### 2) Run Dash app

```bash
PYTHONPATH=src python3 src/smart_grid_lab/ui_dash/app.py
```

Then open `http://127.0.0.1:8050/`.

## Workflow for Development

1. Define/adjust setup in UI (`window1`)
2. Choose `Battery baseline` or `Forecast H₂ control`
3. Run simulation and inspect output figure/KPI table
4. Capture progress in `rnd notes and materials/`
5. Promote stable behavior from callbacks into application/infrastructure
6. Record decisions and assumptions for reproducibility

## Progress Tracking

Use the notes system in `rnd notes and materials/`:
- `00_INDEX.md` for map and usage
- `01_roadmap.md` for strategic steps
- `02_decisions_log.md` for architecture decisions
- `03_experiment_log.md` for experiment-level evidence
- `04_media_strategy.md` for communication/publication workflow

## Upcoming Strategic Step

Define an industrial use case and implement gradually:

- Compare oracle vs rolling surplus forecast control in the UI
- Add explicit curtailment and residual-energy KPIs for the H₂ scenario
- Replace synthetic heuristics with infrastructure-backed trained forecasters when model artifacts exist

## Contributing

Early stage and evolving quickly.  
If you want to collaborate or review scenarios, open an issue or share feedback with context:
- use case,
- assumptions,
- expected outputs,
- validation criteria.
