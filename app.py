import streamlit as st
import matplotlib.pyplot as plt

from calculations import *
from data import *

st.set_page_config(page_title="Hyderabad Solar Advisor", layout="centered")

# ---------------- FORMATTER ---------------- #

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


# ---------------- HEADER ---------------- #

st.title("☀️ Hyderabad Solar Energy Advisor")
st.caption("Data-driven solar performance, ROI, and lifestyle impact analysis")

# ---------------- HOUSE ---------------- #

st.header("🏠 Household Profile")

col1, col2 = st.columns(2)

with col1:
    monthly_units = st.number_input("Monthly Electricity Consumption (kWh)", value=300)

with col2:
    shadow_area = st.slider("Shadow-free Roof Area (m²)", 10, 200, 50)

st.subheader("🚗 Electric Mobility")

col1, col2 = st.columns(2)

with col1:
    car_km = st.slider("Monthly EV Car Usage (km)", 0, 3000, 0)

with col2:
    bike_km = st.slider("Monthly EV Bike Usage (km)", 0, 2000, 0)

# ---------------- SOLAR CONFIG ---------------- #

st.header("☀️ Solar System Configuration")

mode = st.selectbox(
    "System Sizing Strategy",
    ["area", "demand", "budget"]
)

col1, col2 = st.columns(2)

with col1:
    panel_type = st.selectbox("Panel Type", ["monocrystalline", "polycrystalline", "bifacial"])

with col2:
    panel_wattage = st.slider("Panel Wattage (W)", 300, 600, 500)

col1, col2 = st.columns(2)

with col1:
    orientation = st.selectbox("Orientation", ["south", "east_west", "north"])

with col2:
    tilt_factor = st.slider("Tilt Efficiency Factor", 0.8, 1.0, 0.95)

budget = None

if mode == "budget":
    budget = st.number_input("Budget (₹)", value=200000)

if mode == "demand":
    st.info("System will be sized to match your consumption")

# ---------------- CALCULATIONS ---------------- #

ev_data = calculate_ev_load(car_km, bike_km)

ev_monthly = ev_data["monthly"]
ev_yearly = ev_data["yearly"]

annual_consumption = (monthly_units * 12) + ev_yearly

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

annual_generation = calculate_annual_generation(monthly_generation)



monthly_consumption = calculate_monthly_consumption(
    monthly_units,
    ev_monthly
)

monthly_split = calculate_monthly_energy_split(
    monthly_generation,
    monthly_consumption
)

total_usable, total_excess = aggregate_yearly_from_monthly(monthly_split)

financials = calculate_financials(
    total_usable,
    total_excess,
    monthly_units,
    system_size
)

system_cost = calculate_system_cost(system_size, panel_type)

roi = calculate_roi(system_cost, financials["net_benefit"])

insights = generate_insights(
    annual_generation,
    annual_consumption,
    total_usable,
    total_excess,
    roi,
    system_size
)

monthly_financials = calculate_monthly_financials(
    monthly_split,
    financials["tariff"]
)

# ---------------- SYSTEM ---------------- #

st.header("🔌 System Overview")

st.metric("System Size (kW)", f"{system_size:.2f}")
st.metric("Panels Installed", num_panels)

max_panels = int(shadow_area / PANEL_DATA["panel_dimensions"]["standard_area_m2"])
roof_usage = (num_panels / max_panels) * 100 if max_panels else 0

st.metric("Roof Utilization (%)", f"{roof_usage:.1f}")

# ---------------- ENERGY ---------------- #

st.header("⚡ Energy Summary")

col1, col2 = st.columns(2)

with col1:
    st.metric("Annual Generation (kWh)", format_indian_number(annual_generation))

with col2:
    st.metric("Annual Consumption (kWh)", format_indian_number(annual_consumption))

# ---------------- FINANCIAL ---------------- #

st.header("💰 Financial Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Annual Savings (₹)", format_indian_number(financials["savings"]))

with col2:
    st.metric("Export Income (₹)", format_indian_number(financials["export_income"]))

with col3:
    st.metric("Maintenance (₹)", format_indian_number(financials["maintenance"]))

st.metric("Net Benefit (₹)", format_indian_number(financials["net_benefit"]))
st.metric("System Cost (₹)", format_indian_number(system_cost))

if roi:
    st.metric("Payback (Years)", f"{roi:.1f}")

# ---------------- MONTHLY ---------------- #

st.header("📅 Monthly Analysis")

table_data = []

for m in monthly_split:
    table_data.append({
        "Month": m,
        "Generation": round(monthly_split[m]["generation"]),
        "Consumption": round(monthly_split[m]["consumption"]),
        "Used": round(monthly_split[m]["usable"]),
        "Excess": round(monthly_split[m]["excess"]),
        "Savings (₹)": format_indian_number(monthly_financials[m]["savings"])
    })

st.dataframe(table_data)

# ---------------- GRAPH ---------------- #

months = list(monthly_split.keys())

generation = [monthly_split[m]["generation"] for m in months]
total_consumption_vals = [monthly_split[m]["consumption"] for m in months]

# split consumption into base + EV
base_consumption = [monthly_units for _ in months]
ev_consumption = [ev_monthly for _ in months]

plt.figure()
plt.plot(months, generation, label="Generation")
plt.plot(months, total_consumption_vals, label="Total Consumption")
plt.plot(months, ev_consumption, linestyle='--', label="EV Consumption")

plt.legend()
plt.xticks(rotation=45)
plt.title("Monthly Energy (EV Impact Visible)")

st.pyplot(plt)

# ---------------- INSIGHT ---------------- #

st.header("💡 Smart Insights")

for insight in insights:
    st.write(insight)

st.write("Solar performs best when generation matches consumption.")

st.subheader("🚗 EV Impact")

st.metric("EV Monthly Consumption (kWh)", f"{ev_monthly:.1f}")
st.metric("EV Annual Consumption (kWh)", f"{ev_yearly:.0f}")

if ev_monthly > 0:
    st.info("🚗 EV usage increases solar utilization and reduces wasted energy.")

if roi and roi < 6:
    st.success("Excellent ROI")

elif roi and roi < 10:
    st.info("Moderate ROI")

else:
    st.warning("Long payback period — consider resizing system")

    st.subheader("🔍 System Analysis")

self_use_ratio = total_usable / annual_generation if annual_generation else 0

st.write(f"Self-consumption ratio: {self_use_ratio:.2f}")
st.write(f"Generation vs Consumption ratio: {(annual_generation / annual_consumption):.2f}")
