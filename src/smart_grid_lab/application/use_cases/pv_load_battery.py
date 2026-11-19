"""
Use case: Control of Microgrid with PV, Load and Batterty
for experiment description see:
    rnd notes and materials/use_cases/PV-LOAD-BATTERY.md
"""

from pandas import Series, DataFrame

from smart_grid_lab.core import (
    Time,
    PV,
    Load,
    Grid,
    SetUp,
    Simulation,
    Results,
)

from smart_grid_lab.core.tariff import generate_smooth_tariff_series

from .forecasting import PVForecastModel, LoadForecastModel

from smart_grid_lab.core.controllers import MPC

from smart_grid_lab.domain.microgrid_configuration import PV_AREA_M2

from ..load_template import (
    default_time,
    synthetic_irradiance,
    synthetic_load_kW,
)
from smart_grid_lab.domain.microgrid_configuration import BatteryConfig
from smart_grid_lab.domain.builders import (
    build_battery,
)


def run_simulation(
    time: Time | None = None,
    pv_kw: Series | None = None,
    load_kw: Series | None = None,
    battery_config: BatteryConfig | None = None,
    grid: Grid | None = None,
    tariff: DataFrame | None = None,
    perfect_forecasts: bool | None = None,
    pv_model: PVForecastModel | None = None,
    load_model: LoadForecastModel | None = None,
    controller: MPC | None = None,
    use_bar=False,
) -> Results:

    time = time if time is not None else default_time()
    index = time.index_range

    pv_kw = (
        pv_kw
        if pv_kw is not None
        else synthetic_irradiance(time) * PV_AREA_M2 / 1000.0
    )
    pv_kw = pv_kw.reindex(index).astype(float)

    load_kw = load_kw if load_kw is not None else synthetic_load_kW(time)
    load_kw = load_kw.reindex(index).astype(float)

    battery_config = (
        battery_config if battery_config is not None else BatteryConfig()
    )
    battery = build_battery(battery_config)

    grid = grid if grid is not None else Grid()

    components = {
        "pv": PV(pv_kw),
        "load": Load(load_kw),
        "battery": battery,
        "grid": grid,
    }

    tariff = (
        tariff
        if tariff is not None
        else generate_smooth_tariff_series(
            start=time.start,
            end=time.end,
            sample_interval=time.step,
        )
    )

    setup = SetUp(
        time=time,
        components=components,
        perfect_forecasts=perfect_forecasts,
        pv_model=pv_model,
        load_model=load_model,
        tarif_model=tariff,
    )

    controller = controller if controller is not None else MPC(battery_config)

    simulation = Simulation(setup, controller)

    trajectory = simulation.run(use_bar=use_bar)

    metrics = calculate_metrics(trajectory, tariff, battery.capacity_kwh)
    metrics = format_metrics_table(metrics, case_name="Reactive Control")

    return Results(trajectory=trajectory, metrics=metrics)


def calculate_metrics(
    trajectory: DataFrame,
    tariff: DataFrame,
    nominal_battery_capacity_kwh: float = None,
) -> dict:
    """
    Calculates comprehensive performance and economic metrics for a microgrid simulation.

    Args:
        trajectory: Timestamp-indexed DataFrame with power flows (kW) and SOC.
        tariff: Timestamp-indexed DataFrame with import/export prices (ct/kWh).
        nominal_battery_capacity_kwh: Optional. Required to calculate battery cycles.

    Returns:
        dict: A dictionary containing all calculated metrics.
    """
    # 1. Ensure indices are aligned and sorted
    # We use an inner join to ensure we only calculate where we have both power and price data
    combined = trajectory.join(tariff, how="inner").sort_index()

    if combined.empty:
        raise ValueError(
            "No overlapping timestamps found between trajectory and tariff."
        )

    # 2. Calculate time step (dt) in hours for energy integration
    # Using bfill() ensures the first row gets a valid dt (same as the second row)
    dt_seconds = combined.index.to_series().diff().dt.total_seconds().bfill()
    dt_hours = dt_seconds / 3600.0

    # 3. Energy Calculations (kWh)
    grid_import_energy_kwh = (combined["grid_import_power"] * dt_hours).sum()
    grid_export_energy_kwh = (combined["grid_export_power"] * dt_hours).sum()
    pv_generated_energy_kwh = (combined["pv_power"] * dt_hours).sum()
    battery_charge_energy_kwh = (
        combined["battery_charge_power"] * dt_hours
    ).sum()

    # 4. Peak Calculations (kW)
    grid_import_peak_kw = combined["grid_import_power"].max()

    # 5. Economic Calculations (Cost in cents, then converted to EUR)
    import_cost_ct = (
        combined["grid_import_power"]
        * dt_hours
        * combined["import_price_ct_per_kwh"]
    ).sum()
    export_revenue_ct = (
        combined["grid_export_power"]
        * dt_hours
        * combined["export_price_ct_per_kwh"]
    ).sum()
    net_cost_ct = import_cost_ct - export_revenue_ct

    # 6. PV Utilization (Self-Consumption Rate %)
    # Proxy: Total PV generated minus what was exported to the grid
    pv_self_consumed_kwh = pv_generated_energy_kwh - grid_export_energy_kwh
    pv_utilization_pct = (
        (pv_self_consumed_kwh / pv_generated_energy_kwh * 100)
        if pv_generated_energy_kwh > 0
        else 0.0
    )

    # 7. Battery Metrics
    battery_throughput_kwh = battery_charge_energy_kwh
    battery_cycles = 0.0
    if nominal_battery_capacity_kwh and nominal_battery_capacity_kwh > 0:
        battery_cycles = battery_throughput_kwh / nominal_battery_capacity_kwh

    # 8. Violation Metrics
    # Assuming violation columns are in kW.
    # Energy = integral of power. Count = number of timestamps where violation > 0.
    import_violation_energy_kwh = (
        combined["grid_import_limit_violation"] * dt_hours
    ).sum()
    import_violation_count = (
        combined["grid_import_limit_violation"] > 0.01
    ).sum()  # >0.01 to avoid float noise

    export_violation_energy_kwh = (
        combined["grid_export_limit_violation"] * dt_hours
    ).sum()
    export_violation_count = (
        combined["grid_export_limit_violation"] > 0.01
    ).sum()

    # 9. Compile Results
    metrics = {
        "Total Net Cost (EUR)": round(net_cost_ct / 100.0, 2),
        "Import Cost (EUR)": round(import_cost_ct / 100.0, 2),
        "Export Revenue (EUR)": round(export_revenue_ct / 100.0, 2),
        "Grid Import Energy (kWh)": round(grid_import_energy_kwh, 2),
        "Grid Import Peak (kW)": round(grid_import_peak_kw, 2),
        "PV Utilization / Self-Consumption (%)": round(pv_utilization_pct, 1),
        "Battery Throughput (kWh)": round(battery_throughput_kwh, 2),
        "Battery Equivalent Cycles": round(battery_cycles, 2),
        "Import Violations (Events)": int(import_violation_count),
        "Import Violations (Energy kWh)": round(
            import_violation_energy_kwh, 2
        ),
        "Export Violations (Events)": int(export_violation_count),
        "Export Violations (Energy kWh)": round(
            export_violation_energy_kwh, 2
        ),
        "Total PV Generated (kWh)": round(pv_generated_energy_kwh, 2),
        "Total Grid Exported (kWh)": round(grid_export_energy_kwh, 2),
    }

    return metrics


def format_metrics_table(metrics_dict: dict, case_name) -> DataFrame:
    """Converts the metrics dictionary into a clean, readable pandas DataFrame."""
    df = DataFrame.from_dict(metrics_dict, orient="index", columns=[case_name])
    df.index.name = "Metric"
    return df
