# calculations.py

from data import *

# -----------------------------
# 1. SYSTEM DESIGN
# -----------------------------

def calculate_system_size(
    shadow_free_area,
    panel_type,
    panel_wattage,
    mode="area",
    annual_consumption=None,
    budget=None
):
    panel_info = PANEL_DATA["panel_types"][panel_type]

    panel_area = PANEL_DATA["panel_dimensions"]["standard_area_m2"]

    max_panels = int(shadow_free_area / panel_area)

    if mode == "area":
        num_panels = max_panels

    elif mode == "demand" and annual_consumption:
        pr = sum(LOSS_FACTORS["performance_ratio"]) / 2
        avg_irr = sum(SOLAR_RESOURCE["monthly_irradiance"].values()) / 12

        required_kw = annual_consumption / (avg_irr * 365 * pr)
        num_panels = int((required_kw * 1000) / panel_wattage)

        num_panels = min(num_panels, max_panels)

    elif mode == "budget" and budget:
        cost_per_watt = sum(panel_info["cost_per_watt"]) / 2
        cost_per_kw = cost_per_watt * 1000

        system_kw = budget / cost_per_kw
        num_panels = int((system_kw * 1000) / panel_wattage)

        num_panels = min(num_panels, max_panels)

    else:
        num_panels = max_panels

    system_size_kw = (num_panels * panel_wattage) / 1000

    return num_panels, system_size_kw


# -----------------------------
# 2. GENERATION MODEL
# -----------------------------

def calculate_monthly_generation(system_size_kw, panel_type, orientation="south", tilt_factor=1.0):
    irradiance = SOLAR_RESOURCE["monthly_irradiance"]

    orientation_factor = PANEL_DATA["orientation_factor"][orientation]
    performance_ratio = sum(LOSS_FACTORS["performance_ratio"]) / 2

    panel_performance_factor = {
        "monocrystalline": 1.0,
        "polycrystalline": 0.9,
        "bifacial": 1.1
    }

    monthly_generation = {}

    for month, irr in irradiance.items():
        energy = system_size_kw * irr * 30
        energy *= performance_ratio * orientation_factor * tilt_factor
        energy *= panel_performance_factor[panel_type]

        monthly_generation[month] = energy

    return monthly_generation


def calculate_annual_generation(monthly_generation):
    return sum(monthly_generation.values())


# -----------------------------
# 3. CONSUMPTION MODEL
# -----------------------------

def calculate_appliance_load(num_ac=1, num_geyser=1, num_fridge=1):
    ac_load = num_ac * sum(APPLIANCE_DATA["ac"]) / 2
    geyser_load = num_geyser * sum(APPLIANCE_DATA["geyser"]) / 2
    fridge_load = num_fridge * sum(APPLIANCE_DATA["refrigerator"]) / 2

    return ac_load + geyser_load + fridge_load

def calculate_monthly_consumption(base_monthly_units, ev_monthly):
    factors = MONTHLY_CONSUMPTION_FACTORS

    total_factor = sum(factors.values())

    monthly_consumption = {}

    for month in factors:
        normalized_factor = factors[month] / total_factor

        base_component = base_monthly_units * 12 * normalized_factor
        ev_component = ev_monthly  # constant each month

        monthly_consumption[month] = base_component + ev_component

    return monthly_consumption

def calculate_monthly_energy_split(monthly_generation, monthly_consumption):
    day_ratio = LOAD_PROFILE["usage_split"]["day"]

    monthly_split = {}

    for month in monthly_generation:
        generation = monthly_generation[month]
        consumption = monthly_consumption[month]

        usable = min(generation * day_ratio, consumption)
        excess = max(0, generation - usable)

        monthly_split[month] = {
            "generation": generation,
            "consumption": consumption,
            "usable": usable,
            "excess": excess
        }

    return monthly_split

def calculate_monthly_financials(monthly_split, tariff):
    export_factor = sum(TARIFF_DATA["export_rate_factor"]) / 2
    export_rate = tariff * export_factor

    monthly_financials = {}

    for month, data in monthly_split.items():
        savings = data["usable"] * tariff
        export_income = data["excess"] * export_rate

        monthly_financials[month] = {
            "savings": savings,
            "export_income": export_income,
            "total": savings + export_income
        }

    return monthly_financials

def calculate_ev_load(km_car=0, km_bike=0):
    car_rate = EV_DATA["typical_values"]["car"]
    bike_rate = EV_DATA["typical_values"]["bike"]

    # monthly EV consumption
    car_energy_monthly = km_car * car_rate
    bike_energy_monthly = km_bike * bike_rate

    total_monthly = car_energy_monthly + bike_energy_monthly
    total_yearly = total_monthly * 12

    return {
        "monthly": total_monthly,
        "yearly": total_yearly
    }


def calculate_total_consumption(base_monthly_units, appliance_load, ev_load):
    yearly_base = base_monthly_units * 12
    return yearly_base + appliance_load + ev_load


# -----------------------------
# 4. ENERGY MATCHING
# -----------------------------

def calculate_energy_split(total_generation, total_consumption):
    day_ratio = LOAD_PROFILE["usage_split"]["day"]

    usable_energy = min(total_generation * day_ratio, total_consumption)
    excess_energy = max(0, total_generation - usable_energy)

    return usable_energy, excess_energy


# -----------------------------
# 5. FINANCIAL MODEL
# -----------------------------

def get_average_tariff(monthly_units):
    for low, high, rate in TARIFF_DATA["slabs"]:
        if low <= monthly_units <= high:
            return rate
    return 8

def aggregate_yearly_from_monthly(monthly_split):
    total_usable = 0
    total_excess = 0

    for m in monthly_split:
        total_usable += monthly_split[m]["usable"]
        total_excess += monthly_split[m]["excess"]

    return total_usable, total_excess

def calculate_financials(usable_energy, excess_energy, monthly_units, system_size_kw):
    tariff = get_average_tariff(monthly_units)

    export_factor = sum(TARIFF_DATA["export_rate_factor"]) / 2
    export_rate = tariff * export_factor

    savings = usable_energy * tariff
    export_income = excess_energy * export_rate

    maintenance = system_size_kw * sum(FINANCIAL_DATA["maintenance_cost_per_kw_per_year"]) / 2

    total_annual_benefit = savings + export_income - maintenance

    return {
        "tariff": tariff,
        "savings": savings,
        "export_income": export_income,
        "maintenance": maintenance,
        "net_benefit": total_annual_benefit
    }


# -----------------------------
# 6. COST + ROI
# -----------------------------

def calculate_system_cost(system_size_kw, panel_type):
    panel_info = PANEL_DATA["panel_types"][panel_type]

    cost_per_watt = sum(panel_info["cost_per_watt"]) / 2
    cost_per_kw = cost_per_watt * 1000

    return system_size_kw * cost_per_kw


def calculate_roi(system_cost, annual_benefit):
    if annual_benefit <= 0:
        return None
    return system_cost / annual_benefit


# -----------------------------
# 7. LONG TERM MODEL
# -----------------------------

def project_20_years(annual_benefit, system_cost):
    inflation = sum(TARIFF_DATA["electricity_inflation"]) / 2
    degradation = sum(LOSS_FACTORS["degradation"]["annual"]) / 2

    yearly_profit = []
    current_benefit = annual_benefit

    total = 0

    for year in range(1, 21):
        adjusted = current_benefit * ((1 - degradation) ** year) * ((1 + inflation) ** year)
        total += adjusted
        yearly_profit.append(total)

    return yearly_profit


# -----------------------------
# 8. EV + LIFESTYLE INSIGHTS
# -----------------------------

def calculate_ev_support(total_generation):
    car_rate = EV_DATA["typical_values"]["car"]
    bike_rate = EV_DATA["typical_values"]["bike"]

    return {
        "car_km_supported": total_generation / car_rate,
        "bike_km_supported": total_generation / bike_rate
    }

def generate_insights(
    total_generation,
    total_consumption,
    usable_energy,
    excess_energy,
    roi,
    system_size_kw
):
    insights = []

    # -------------------------
    # 1. Over / Under sizing
    # -------------------------
    if total_generation > total_consumption * 1.2:
        insights.append("⚠️ Your system is oversized. A large portion of energy is being exported at lower rates.")

    elif total_generation < total_consumption * 0.7:
        insights.append("⚠️ Your system is undersized and cannot cover most of your consumption.")

    else:
        insights.append("✅ Your system size is well matched to your consumption.")

    # -------------------------
    # 2. Self-consumption
    # -------------------------
    if total_generation > 0:
        self_use_ratio = usable_energy / total_generation

        if self_use_ratio < 0.5:
            insights.append("⚡ Low self-consumption. Most energy is exported, reducing savings.")

        elif self_use_ratio > 0.8:
            insights.append("💡 High self-consumption. You are using most of your generated energy efficiently.")

    # -------------------------
    # 3. Payback analysis
    # -------------------------
    if roi:
        if roi > 12:
            insights.append("⏳ Long payback period. Consider reducing system size or increasing consumption (e.g., EV usage).")

        elif roi < 6:
            insights.append("🚀 Excellent payback period. This is a strong financial investment.")

    # -------------------------
    # 4. Excess energy suggestion
    # -------------------------
    if excess_energy > usable_energy:
        insights.append("🔋 Consider adding battery storage or increasing usage (EVs, appliances) to utilize excess energy.")

    # -------------------------
    # 5. EV opportunity
    # -------------------------
    if excess_energy > 1000:
        insights.append("🚗 Your excess solar energy can significantly support EV charging and reduce fuel costs.")

    return insights
