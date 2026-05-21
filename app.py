import streamlit as st
import matplotlib.pyplot as plt

from calculations import *
from data import *

st.set_page_config(
    page_title="Hyderabad Solar Advisor",
    layout="centered"
)

# ---------------------------------
# FORMATTER
# ---------------------------------

def format_indian_number(num):

    num = int(num)

    s = str(num)

    if len(s) <= 3:
        return s

    last3 = s[-3:]

    rest = s[:-3]

    parts = []

    while len(rest) > 2:

        parts.insert(0, rest[-2:])

        rest = rest[:-2]

    if rest:
        parts.insert(0, rest)

    return ",".join(parts) + "," + last3


# ---------------------------------
# HEADER
# ---------------------------------

st.title("☀️ Hyderabad Solar Energy Advisor")

st.caption(
    "Realistic residential rooftop solar sizing and ROI analysis for Hyderabad households"
)

# ---------------------------------
# HOUSEHOLD PROFILE
# ---------------------------------

st.header("🏠 Household Profile")

col1, col2 = st.columns(2)

with col1:

    monthly_units = st.number_input(
        "Monthly Electricity Consumption (kWh)",
        min_value=50,
        max_value=3000,
        value=350,
        step=50
    )

with col2:

    shadow_area = st.slider(
        "Shadow-free Roof Area (m²)",
        10,
        300,
        60
    )

# ---------------------------------
# EV SECTION
# ---------------------------------

st.subheader("🚗 Electric Mobility")

col1, col2 = st.columns(2)

with col1:

    car_km = st.slider(
        "Monthly EV Car Usage (km)",
        0,
        3000,
        0
    )

with col2:

    bike_km = st.slider(
        "Monthly EV Bike Usage (km)",
        0,
        2000,
        0
    )

# ---------------------------------
# SOLAR CONFIGURATION
# ---------------------------------

st.header("☀️ Solar System Configuration")

mode = st.selectbox(
    "System Sizing Strategy",
    ["demand", "area", "budget"]
)

col1, col2 = st.columns(2)

with col1:

    panel_type = st.selectbox(
        "Panel Type",
        [
            "monocrystalline",
            "polycrystalline",
            "bifacial"
        ]
    )

with col2:

    panel_wattage = st.slider(
        "Panel Wattage (W)",
        400,
        650,
        550
    )

col1, col2 = st.columns(2)

with col1:

    orientation = st.selectbox(
        "Orientation",
        [
            "south",
            "east_west",
            "north"
        ]
    )

with col2:

    tilt_factor = st.slider(
        "Tilt Efficiency Factor",
        0.85,
        1.0,
        0.95
    )

budget = None

if mode == "budget":

    budget = st.number_input(
        "Budget (₹)",
        value=200000,
        step=50000
    )

if mode == "demand":

    st.info(
        "System will be sized based on your electricity usage."
    )

# ---------------------------------
# CALCULATIONS
# ---------------------------------

ev_data = calculate_ev_load(
    car_km,
    bike_km
)

ev_monthly = ev_data["monthly"]

ev_yearly = ev_data["yearly"]

annual_consumption = (
    monthly_units * 12
) + ev_yearly

num_panels, system_size = calculate_system_size(
    shadow_area,
    panel_type,
    panel_wattage,
    mode=mode,
    annual_consumption=annual_consumption,
    budget=budget
)

monthly_generation = calculate_monthly_generation(
    system_size,
    panel_type,
    orientation,
    tilt_factor
)

annual_generation = calculate_annual_generation(
    monthly_generation
)

monthly_consumption = calculate_monthly_consumption(
    monthly_units,
    ev_monthly
)

monthly_split = calculate_monthly_energy_split(
    monthly_generation,
    monthly_consumption
)

total_usable, total_excess = aggregate_yearly_from_monthly(
    monthly_split
)

financials = calculate_financials(
    total_usable,
    total_excess,
    monthly_units,
    system_size
)

system_cost = calculate_system_cost(
    system_size,
    panel_type
)

roi = calculate_roi(
    system_cost,
    financials["net_benefit"]
)

insights = generate_insights(
    annual_generation,
    annual_consumption,
    total_usable,
    total_excess,
    roi,
    system_size
)

# ---------------------------------
# SYSTEM OVERVIEW
# ---------------------------------

st.header("🔌 System Overview")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "System Size (kW)",
        f"{system_size:.2f}"
    )

with col2:

    st.metric(
        "Panels Installed",
        num_panels
    )

with col3:

    used_area = (
        num_panels
        * PANEL_DATA["panel_dimensions"]["standard_area_m2"]
    )

    roof_usage = (
        used_area / shadow_area
    ) * 100 if shadow_area else 0

    st.metric(
        "Roof Usage (%)",
        f"{roof_usage:.1f}"
    )

# ---------------------------------
# ENERGY SUMMARY
# ---------------------------------

st.header("⚡ Energy Summary")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Annual Generation (kWh)",
        format_indian_number(annual_generation)
    )

with col2:

    st.metric(
        "Annual Consumption (kWh)",
        format_indian_number(annual_consumption)
    )

generation_ratio = (
    annual_generation / annual_consumption
)

st.progress(
    min(generation_ratio, 1.0)
)

st.caption(
    f"Solar offset ratio: {generation_ratio:.2f}x"
)

# ---------------------------------
# FINANCIAL SUMMARY
# ---------------------------------

st.header("💰 Financial Summary")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Annual Savings (₹)",
        format_indian_number(
            financials["savings"]
        )
    )

with col2:

    st.metric(
        "Export Income (₹)",
        format_indian_number(
            financials["export_income"]
        )
    )

with col3:

    st.metric(
        "Maintenance (₹)",
        format_indian_number(
            financials["maintenance"]
        )
    )

st.metric(
    "Net Annual Benefit (₹)",
    format_indian_number(
        financials["net_benefit"]
    )
)

st.metric(
    "Estimated System Cost (₹)",
    format_indian_number(
        system_cost
    )
)

if roi:

    st.metric(
        "Payback Period (Years)",
        f"{roi:.1f}"
    )

# ---------------------------------
# MONTHLY TABLE
# ---------------------------------

st.header("📅 Monthly Analysis")

table_data = []

tariff = financials["tariff"]

for month in monthly_split:

    savings = (
        monthly_split[month]["usable"]
        * tariff
    )

    table_data.append({

        "Month": month,

        "Generation": round(
            monthly_split[month]["generation"]
        ),

        "Consumption": round(
            monthly_split[month]["consumption"]
        ),

        "Used": round(
            monthly_split[month]["usable"]
        ),

        "Excess": round(
            monthly_split[month]["excess"]
        ),

        "Savings (₹)": format_indian_number(
            savings
        )
    })

st.dataframe(
    table_data,
    use_container_width=True
)

# ---------------------------------
# GRAPH
# ---------------------------------

st.header("📈 Monthly Energy Profile")

months = list(monthly_split.keys())

generation = [
    monthly_split[m]["generation"]
    for m in months
]

consumption = [
    monthly_split[m]["consumption"]
    for m in months
]

plt.figure(figsize=(10, 5))

plt.plot(
    months,
    generation,
    marker='o',
    label="Solar Generation"
)

plt.plot(
    months,
    consumption,
    marker='o',
    label="Consumption"
)

plt.xticks(rotation=45)

plt.ylabel("kWh")

plt.title(
    "Monthly Solar Generation vs Consumption"
)

plt.legend()

st.pyplot(plt)

# ---------------------------------
# SMART INSIGHTS
# ---------------------------------

st.header("💡 Smart Insights")

for insight in insights:

    st.write(insight)

# ---------------------------------
# EV IMPACT
# ---------------------------------

st.header("🚗 EV Impact")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "EV Monthly Consumption (kWh)",
        f"{ev_monthly:.1f}"
    )

with col2:

    st.metric(
        "EV Annual Consumption (kWh)",
        f"{ev_yearly:.0f}"
    )

if ev_monthly > 0:

    st.info(
        "EV charging improves daytime solar utilization."
    )

# ---------------------------------
# FINAL ANALYSIS
# ---------------------------------

st.header("🔍 System Analysis")

self_use_ratio = (
    total_usable / annual_generation
) if annual_generation else 0

st.write(
    f"Self-consumption ratio: {self_use_ratio:.2f}"
)

st.write(
    f"Generation vs Consumption ratio: {generation_ratio:.2f}"
)

if generation_ratio > 1.3:

    st.warning(
        "Your system may be oversized for your current usage."
    )

elif generation_ratio < 0.75:

    st.warning(
        "Your system may not fully offset your electricity usage."
    )

else:

    st.success(
        "Your solar system sizing appears well balanced."
    )
