# Post Draft - Forecast H₂ Control UI Slice

## Short LinkedIn-style version

This week I moved Smart Grid Lab one step closer to an experimentation platform: the Dash UI can now run a forecast-based hydrogen control use case on synthetic data.

What changed:
- the setup panel now lets me switch between a battery baseline and forecast-informed H₂ control;
- the H₂ mode wires the UI into the application use case instead of duplicating simulation loops in callbacks;
- synthetic solar/load profiles drive an off-grid scenario with battery, electrolyser, and hydrogen tank;
- the result chart now shows electrolyser power and tank level alongside solar, load, and battery behavior;
- the KPI table reports energy totals, hydrogen produced, final tank level, final battery SOC, and an electrolyser degradation proxy.

The important architecture point: UI remains thin. It calls the application layer, which composes the forecast model and control strategy, then the core `Simulation` steps all components.

This is still an early synthetic benchmark, not a validated plant model. The next steps are side-by-side forecast comparisons, explicit curtailment KPIs, and later infrastructure-backed trained forecasters.

If you work on microgrid control, hydrogen systems, or forecasting, what benchmark scenario would you test next?

## Technical notes for follow-up post

- Current forecast choices: oracle mean surplus for debugging and rolling mean surplus as a causal baseline.
- Current limitation: PV area is still fixed at 100 m² in the `Solar` component, so the UI converts synthetic irradiance to kW using that same assumption.
- Good visual asset: screenshot of `window1` after selecting `Forecast H₂ control` and running the default synthetic scenario.
