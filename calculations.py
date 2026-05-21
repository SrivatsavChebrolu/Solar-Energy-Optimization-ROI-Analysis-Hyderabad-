from data import *

# -----------------------------
# SYSTEM SIZING
# -----------------------------

def calculate_system_size(
    shadow_free_area,
    panel_type,
    panel_wattage,
    mode="area",
    annual_consumption=None,
    budget=None
):

    panel_area = PANEL_DATA["panel_dimensions"]["standard_area_m2"]

    max_panels = int(
        shadow_free_area / panel_area
    )

    generation_per_kw_year = 1550

    performance_ratio = sum(
        LOSS_FACTORS["performance_ratio"]
    ) / 2

    effective_generation = (
        generation_per_kw_year
        * performance_ratio
    )

    # -----------------------------
    # DEMAND-BASED IDEAL SIZE
    # -----------------------------

    ideal_kw = None

    if annual_consumption:

        ideal_kw = (
            annual_consumption
            / effective_generation
        )

        # 10% safety margin
        ideal_kw *= 1.1

    # -----------------------------
    # AREA MODE
    # -----------------------------

    if mode == "area":

        roof_max_kw = (
            max_panels * panel_wattage
        ) / 1000

        # avoid extreme oversizing
        if ideal_kw:

            system_size_kw = min(
                roof_max_kw,
                ideal_kw * 1.25
            )

        else:

            system_size_kw = roof_max_kw

    # -----------------------------
    # DEMAND MODE
    # -----------------------------

    elif mode == "demand" and annual_consumption:

        system_size_kw = ideal_kw

    # -----------------------------
    # BUDGET MODE
    # -----------------------------

    elif mode == "budget" and budget:

        avg_cost_per_kw = sum(
            FINANCIAL_DATA[
                "cost_per_kw_post_subsidy"
            ]
        ) / 2

        affordable_kw = (
            budget / avg_cost_per_kw
        )

        if ideal_kw:

            # don't oversize heavily
            system_size_kw = min(
                affordable_kw,
                ideal_kw * 1.2
            )

        else:

            system_size_kw = affordable_kw

    else:

        system_size_kw = (
            max_panels * panel_wattage
        ) / 1000

    # -----------------------------
    # PANEL COUNT
    # -----------------------------

    num_panels = int(
        (system_size_kw * 1000)
        / panel_wattage
    )

    num_panels = min(
        num_panels,
        max_panels
    )

    system_size_kw = (
        num_panels * panel_wattage
    ) / 1000

    return num_panels, round(system_size_kw, 2)


# -----------------------------
# GENERATION
# -----------------------------

def calculate_monthly_generation(
    system_size_kw,
    panel_type,
    orientation="south",
    tilt_factor=1.0
):
    irradiance = SOLAR_RESOURCE["monthly_irradiance"]

    orientation_factor = (
        PANEL_DATA["orientation_factor"][orientation]
    )

    performance_ratio = sum(
        LOSS_FACTORS["performance_ratio"]
    ) / 2

    panel_performance_factor = {
        "monocrystalline": 1.0,
        "polycrystalline": 0.94,
        "bifacial": 1.05
    }

    monthly_generation = {}

    for month, irr in irradiance.items():

        days = 30

        energy = (
            system_size_kw
            * irr
            * days
            * performance_ratio
            * orientation_factor
            * tilt_factor
            * panel_performance_factor[panel_type]
        )

        monthly_generation[month] = round(
            energy,
            2
        )

    return monthly_generation


def calculate_annual_generation(
    monthly_generation
):
    return round(
        sum(monthly_generation.values()),
        2
    )


# -----------------------------
# EV LOAD
# -----------------------------

def calculate_ev_load(
    km_car=0,
    km_bike=0
):
    car_rate = EV_DATA["typical_values"]["car"]
    bike_rate = EV_DATA["typical_values"]["bike"]

    car_energy_monthly = km_car * car_rate
    bike_energy_monthly = km_bike * bike_rate

    total_monthly = (
        car_energy_monthly + bike_energy_monthly
    )

    total_yearly = total_monthly * 12

    return {
        "monthly": round(total_monthly, 2),
        "yearly": round(total_yearly, 2)
    }


# -----------------------------
# MONTHLY CONSUMPTION
# -----------------------------

def calculate_monthly_consumption(
    base_monthly_units,
    ev_monthly
):
    factors = MONTHLY_CONSUMPTION_FACTORS

    total_factor = sum(factors.values())

    monthly_consumption = {}

    for month in factors:

        normalized_factor = (
            factors[month] / total_factor
        )

        base_component = (
            base_monthly_units
            * 12
            * normalized_factor
        )

        monthly_consumption[month] = round(
            base_component + ev_monthly,
            2
        )

    return monthly_consumption


# -----------------------------
# ENERGY SPLIT
# -----------------------------

def calculate_monthly_energy_split(
    monthly_generation,
    monthly_consumption
):
    day_ratio = (
        LOAD_PROFILE["usage_split"]["day"]
    )

    monthly_split = {}

    for month in monthly_generation:

        generation = monthly_generation[month]

        consumption = monthly_consumption[month]

        usable = min(
            generation * day_ratio,
            consumption
        )

        excess = max(
            0,
            generation - usable
        )

        monthly_split[month] = {
            "generation": generation,
            "consumption": consumption,
            "usable": round(usable, 2),
            "excess": round(excess, 2)
        }

    return monthly_split


def aggregate_yearly_from_monthly(
    monthly_split
):
    total_usable = 0
    total_excess = 0

    for month in monthly_split:

        total_usable += monthly_split[month]["usable"]

        total_excess += monthly_split[month]["excess"]

    return round(total_usable, 2), round(total_excess, 2)


# -----------------------------
# TARIFF
# -----------------------------

def get_average_tariff(
    monthly_units
):
    for low, high, rate in TARIFF_DATA["slabs"]:

        if low <= monthly_units <= high:
            return rate

    return 8


# -----------------------------
# FINANCIALS
# -----------------------------

def calculate_financials(
    usable_energy,
    excess_energy,
    monthly_units,
    system_size_kw
):
    tariff = get_average_tariff(
        monthly_units
    )

    export_factor = sum(
        TARIFF_DATA["export_rate_factor"]
    ) / 2

    export_rate = tariff * export_factor

    savings = usable_energy * tariff

    export_income = (
        excess_energy * export_rate
    )

    maintenance = (
        system_size_kw
        * sum(
            FINANCIAL_DATA[
                "maintenance_cost_per_kw_per_year"
            ]
        ) / 2
    )

    total_annual_benefit = (
        savings
        + export_income
        - maintenance
    )

    return {
        "tariff": round(tariff, 2),
        "savings": round(savings),
        "export_income": round(export_income),
        "maintenance": round(maintenance),
        "net_benefit": round(
            total_annual_benefit
        )
    }


# -----------------------------
# COST
# -----------------------------

def calculate_system_cost(
    system_size_kw,
    panel_type
):
    avg_cost_per_kw = sum(
        FINANCIAL_DATA[
            "cost_per_kw_post_subsidy"
        ]
    ) / 2

    base_cost = (
        system_size_kw * avg_cost_per_kw
    )

    subsidy = 0

    if system_size_kw <= 2:

        subsidy = 30000

    elif system_size_kw <= 3:

        subsidy = 48000

    else:

        subsidy = 78000

    final_cost = max(
        base_cost - subsidy,
        0
    )

    return round(final_cost)


# -----------------------------
# ROI
# -----------------------------

def calculate_roi(
    system_cost,
    annual_benefit
):
    if annual_benefit <= 0:
        return None

    return round(
        system_cost / annual_benefit,
        1
    )


# -----------------------------
# LONG TERM PROJECTION
# -----------------------------

def project_20_years(
    annual_benefit,
    system_cost
):
    inflation = sum(
        TARIFF_DATA["electricity_inflation"]
    ) / 2

    degradation = sum(
        LOSS_FACTORS["degradation"]["annual"]
    ) / 2

    yearly_profit = []

    total = 0

    for year in range(1, 21):

        adjusted = (
            annual_benefit
            * ((1 - degradation) ** year)
            * ((1 + inflation) ** year)
        )

        total += adjusted

        yearly_profit.append(round(total))

    return yearly_profit


# -----------------------------
# EV SUPPORT
# -----------------------------

def calculate_ev_support(
    total_generation
):
    car_rate = EV_DATA["typical_values"]["car"]

    bike_rate = EV_DATA["typical_values"]["bike"]

    return {
        "car_km_supported": round(
            total_generation / car_rate
        ),

        "bike_km_supported": round(
            total_generation / bike_rate
        )
    }


# -----------------------------
# INSIGHTS
# -----------------------------

def generate_insights(
    total_generation,
    total_consumption,
    usable_energy,
    excess_energy,
    roi,
    system_size_kw
):
    insights = []

    ratio = (
        total_generation / total_consumption
    )

    if ratio > 1.3:

        insights.append(
            "⚠️ Your system appears oversized for your current usage."
        )

    elif ratio < 0.75:

        insights.append(
            "⚠️ Your system may not fully offset your electricity usage."
        )

    else:

        insights.append(
            "✅ Your solar system sizing looks well balanced."
        )

    self_use_ratio = (
        usable_energy / total_generation
    ) if total_generation else 0

    if self_use_ratio < 0.5:

        insights.append(
            "⚡ Low self-consumption detected. Consider shifting appliance usage to daytime."
        )

    elif self_use_ratio > 0.8:

        insights.append(
            "💡 Excellent solar utilization."
        )

    if roi:

        if roi < 6:

            insights.append(
                "🚀 Excellent financial return."
            )

        elif roi < 10:

            insights.append(
                "📈 Moderate long-term investment returns."
            )

        else:

            insights.append(
                "⏳ Long payback period. Consider resizing."
            )

    if excess_energy > 1000:

        insights.append(
            "🚗 Excess solar energy can support EV charging effectively."
        )

    return insights
