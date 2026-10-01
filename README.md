# Smart Grid Lab

**Smart Grid Lab is a Python-based experimental environment for modeling, simulating, and experimenting with microgrid control and energy management strategies.**

The project brings together system configuration, forecasting, control, simulation, and experiment evaluation in one workflow.

> **Configure → Forecast → Control → Simulate → Compare**

The aim is not to provide another power-system simulation tool, but to create an environment where researchers and engineers can **compose models and strategies, run comparable experiments, and study how different decisions affect system behavior.**

The project is currently in an early and evolving stage.

---

## What is Smart Grid Lab?

Many tools focus primarily on one part of the problem:

* power-system simulation,
* optimization,
* forecasting,
* control,
* or data analysis.

Smart Grid Lab explores the space between them.

The central object is an **experimental loop** in which different system models, forecasting methods, and control or decision strategies can be introduced and evaluated under the same simulation workflow.

A simplified view is:

```text
       System configuration
               │
               ▼
       ┌─────────────────┐
       │  Microgrid      │
       │  model          │
       └────────┬────────┘
                │
                ▼
          Data / Forecast
                │
                ▼
       Control / Decision
          strategy
                │
                ▼
          Simulation
                │
                ▼
        Trajectories / KPIs
                │
                ▼
            Comparison
```

This makes Smart Grid Lab closer to an **experimental laboratory** than to a single-purpose simulator.

---

## Current Focus

The current development focuses on energy-management experiments at the **microgrid / plant scale**, particularly systems involving:

* renewable generation,
* electrical loads,
* batteries,
* hydrogen production,
* electrolysers,
* hydrogen storage,
* grid interaction,
* forecasting,
* and control strategies.

The architecture is intended to allow additional components, models, forecasting methods, and strategies to be introduced without redesigning the entire simulation environment.

---

## Current Capabilities

The current implementation provides building blocks for:

### Data

* loading time-series data,
* preprocessing gaps and anomalies,
* preparing data for forecasting and simulation,
* working with open energy datasets.

### Microgrid modeling

A composable component library currently includes models for elements such as:

* PV generation,
* electrical load,
* battery,
* electrolyser,
* hydrogen storage,
* grid interface.

### Simulation

* configurable simulation horizon,
* discrete simulation/control loop,
* component trajectories,
* configurable system composition,
* simulation through application-layer use cases.

### Forecasting

The architecture supports different forecasting approaches through model contracts and adapters.

Current experimentation includes:

* SARIMAX,
* regression-based approaches,
* OpenSTEF integration,
* preparation for additional forecasting models.

### Control

The system supports injecting different control strategies into the simulation loop.

Current experiments include:

* baseline / heuristic strategies,
* forecast-based hydrogen control,
* proactive control based on predicted renewable surplus.

### Evaluation

Experiments can produce:

* power trajectories,
* system-state trajectories,
* hydrogen and electrolyser behavior,
* operational metrics,
* KPI tables,
* visual comparison of strategies.

The current UI is implemented with **Dash**.

---

## Software Architecture

The current architecture separates the simulation domain from application orchestration, infrastructure, and presentation.

```text
┌─────────────────────────────┐
│           UI                │
│         Dash / Notebook     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Application           │
│     experiment / use cases  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│            Core             │
│ simulation + components     │
│ forecasting contracts       │
│ control strategies          │
└──────────────┬──────────────┘
               │
               ▼
        Microgrid model
```

Infrastructure provides adapters for external data, trained forecasting models, persistence, APIs, and other I/O.

The intended dependency direction is:

**UI → Application → Core**

with infrastructure connected at the application/integration boundary.

### Repository structure

```text
src/smart_grid_lab/
├── core/              # simulation engine and domain mechanics
├── application/       # experiment and use-case orchestration
├── infrastructure/    # data, models, persistence and external adapters
├── ui_dash/           # Dash presentation layer
└── domain/             # schemas, builders and validators

rnd notes and materials/
├── research notes
├── experiments
├── architecture decisions
├── roadmap
└── communication materials
```

The architecture is still evolving as experiments reveal which abstractions are actually useful.

---

## What Can I Model or Experiment With?

The current environment can be used to formulate experiments such as:

### Renewable energy and storage

* PV + load + battery systems
* renewable surplus management
* grid-connected and off-grid configurations
* battery charging/discharging strategies

### Hydrogen systems

* PV + load + electrolyser + H₂ storage
* electrolyser dispatch strategies
* renewable-surplus-based hydrogen production
* forecast-informed hydrogen control
* comparison of different control strategies

### Forecasting and control

A forecasting model can be evaluated not only by forecast error, but by the **operational consequences of using that forecast inside a control strategy**.

For example:

```text
Historical / real-time data
          │
          ▼
      Forecast
          │
          ▼
   Control strategy
          │
          ▼
      Simulation
          │
          ▼
 Operational performance
```

This makes it possible to investigate questions such as:

> How much operational value does a better forecast actually provide?

---

## How Could My Model or Problem Plug Into Smart Grid Lab?

One direction of development is to make Smart Grid Lab useful not only with its own models, but as an **experimental environment for external models and solutions**.

For example, an external forecasting system could provide:

```text
Real-time / historical telemetry
              │
              ▼
      External forecast API
              │
              ▼
       Smart Grid Lab
              │
              ▼
       Control strategy
              │
              ▼
          Simulation
```

Similarly, an external decision-support or control solution could receive system state and telemetry and return a control decision:

```text
Microgrid state
      │
      ▼
 Smart Grid Lab
      │
      ├── historical data
      ├── current telemetry
      └── forecast
      │
      ▼
External decision-support API
      │
      ▼
Control decision
      │
      ▼
Simulation / evaluation
```

For open-source tools, integration may eventually be implemented natively where this provides a clear advantage.

For proprietary or externally hosted solutions, HTTP APIs can provide a more general integration boundary.

The goal is to make it possible to evaluate different approaches under comparable experimental conditions rather than requiring every researcher or engineer to build the surrounding simulation infrastructure from scratch.

---

## How to Run an Experiment

### In the Dash UI

Start the application:

```bash
PYTHONPATH=src python3 src/smart_grid_lab/ui_dash/app.py
```

Then open:

```text
http://127.0.0.1:8050/
```

The current workflow is approximately:

1. configure the simulation horizon;
2. configure the microgrid components;
3. select or prepare the input data;
4. select a forecasting/control approach;
5. run the simulation;
6. inspect trajectories and KPIs;
7. compare the resulting behavior.

### In a notebook

The experimental workflow can also be constructed programmatically:

```text
1. Define time horizon and location
2. Load / prepare data
3. Configure microgrid components
4. Select forecasting method
5. Select control strategy
6. Construct microgrid control system
7. Run simulation loop
8. Plot trajectories
9. Calculate and inspect metrics
```

---

## Development Directions

The project is currently developing along two connected directions.

### Energy Systems R&D

Current and planned experiments include:

* PV + battery + load + grid scenarios,
* renewable surplus management,
* forecast-informed control,
* rolling-horizon control / MPC,
* comparison of oracle and rolling forecasts,
* multi-electrolyser control,
* operational KPIs for hydrogen systems,
* new experiments arising from external use cases,
* experiments using open data and open models.

One research question motivating the work is:

> **How does information quality, particularly forecast quality, translate into operational value when it is actually used by a control strategy?**

The answer cannot necessarily be obtained from forecast metrics alone. It depends on the complete chain:

**data → forecast → decision → control → physical system → operational outcome.**

### Software Development

Smart Grid Lab is also exploring integration with the wider open energy-modeling ecosystem.

Tools such as **Power Grid Model, pandapower, and PyPSA** address important problems at different scales and levels of abstraction.

Smart Grid Lab currently focuses more specifically on experimentation with:

* energy-management strategies,
* forecasting,
* control,
* plant-scale dynamics,
* and decision support.

The intention is therefore not to replace existing power-system modeling tools, but potentially to provide an experimental layer around them where appropriate.

---

## Current Challenges

Several parts of the system are still experimental.

Current technical questions include:

* which abstractions are actually useful across different experiments;
* how forecasting and control APIs should be defined;
* how external models should be integrated;
* how experiments should be represented and reproduced;
* which KPIs are meaningful across different use cases;
* how the UI should expose the underlying experimental workflow;
* where native integration is preferable to API-based integration.

These questions are being addressed through implementation and experiments rather than being treated as settled architecture in advance.

---

## How to Contribute

At this stage, useful contributions do not necessarily mean writing code.

You can contribute by:

* proposing an energy-system use case;
* providing or pointing to open real-world data;
* suggesting an existing open model or tool for integration;
* testing an experiment;
* reviewing the architecture;
* identifying useful KPIs or comparison methods;
* contributing a forecasting or control approach;
* discussing how an existing external solution could be integrated.

If you propose an experiment or use case, it is particularly useful to describe:

* the system or problem,
* available data,
* assumptions,
* the strategy or hypothesis to test,
* expected outputs,
* and how the result could be validated.

---

## Project Status

Smart Grid Lab is an **early-stage experimental project**.

The architecture, interfaces, and scope are being refined through actual experiments and interaction with researchers and engineers.

The repository therefore represents both:

1. a working software environment, and
2. an ongoing investigation into how different energy-system models, forecasting methods, and control strategies can be composed and compared.

The most useful question for the project is not only:

> *What can Smart Grid Lab do?*

but also:

> **What experiments become easier, more reproducible, or more informative when these capabilities are brought together in one environment?**

