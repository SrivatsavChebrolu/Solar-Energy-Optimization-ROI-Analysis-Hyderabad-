SOLAR_RESOURCE = {
    "monthly_irradiance": {
        "Jan": 5.2,
        "Feb": 5.6,
        "Mar": 6.2,
        "Apr": 6.5,
        "May": 6.7,
        "Jun": 5.8,
        "Jul": 4.5,
        "Aug": 4.3,
        "Sep": 5.0,
        "Oct": 5.4,
        "Nov": 5.2,
        "Dec": 5.0
    },

    "monthly_sun_hours": {
        "Jan": 9.0,
        "Feb": 8.8,
        "Mar": 9.1,
        "Apr": 9.1,
        "May": 9.4,
        "Jun": 6.0,
        "Jul": 4.7,
        "Aug": 4.5,
        "Sep": 5.6,
        "Oct": 7.5,
        "Nov": 8.1,
        "Dec": 8.7
    },

    "annual_sun_hours": 2730
}


PANEL_DATA = {
    "panel_types": {
        "monocrystalline": {
            "efficiency": (0.19, 0.23),
            "cost_per_watt": (32, 50),
            "typical_wattage": (500, 600)
        },

        "polycrystalline": {
            "efficiency": (0.15, 0.18),
            "cost_per_watt": (28, 42),
            "typical_wattage": (350, 450)
        },

        "bifacial": {
            "efficiency": (0.20, 0.24),
            "cost_per_watt": (45, 65),
            "typical_wattage": (540, 650)
        }
    },

    "panel_dimensions": {
        "standard_area_m2": 2.0,
        "large_panel_area_m2": 2.4
    },

    # Modern 500W+ panels
    "panels_per_kw": (2, 3),

    # Realistic rooftop requirement
    "space_required_per_kw_sqft": (80, 100),

    # Hyderabad optimal tilt
    "tilt_angle_optimal": (15, 20),

    "orientation_factor": {
        "south": 1.0,
        "east_west": 0.88,
        "north": 0.72
    }
}


LOSS_FACTORS = {
    "temperature_loss": (0.08, 0.12),

    # Hyderabad dust conditions with regular cleaning
    "dust_loss": (0.04, 0.10),

    "inverter_loss": (0.02, 0.04),

    "dc_loss": (0.01, 0.02),

    "mismatch_loss": (0.01, 0.02),

    "reflection_loss": (0.01, 0.02),

    # Modern residential rooftop systems
    "total_system_loss": (0.14, 0.18),

    # Typical Indian rooftop PR
    "performance_ratio": (0.80, 0.86),

    "degradation": {
        "initial": 0.02,
        "annual": (0.004, 0.006)
    }
}


TARIFF_DATA = {
    "slabs": [
        (0, 50, 1.95),
        (51, 100, 3.10),
        (101, 200, 4.80),
        (201, 300, 7.70),
        (301, 400, 9.00),
        (401, 800, 9.50),
        (800, float("inf"), 10.00)
    ],

    # Net metering export compensation
    "export_rate_factor": (0.55, 0.65),

    "electricity_inflation": (0.04, 0.06)
}


MONTHLY_CONSUMPTION_FACTORS = {
    "Jan": 0.9,
    "Feb": 0.9,
    "Mar": 1.1,
    "Apr": 1.25,
    "May": 1.35,
    "Jun": 1.15,
    "Jul": 1.0,
    "Aug": 1.0,
    "Sep": 1.0,
    "Oct": 0.95,
    "Nov": 0.9,
    "Dec": 0.9
}


FINANCIAL_DATA = {

    # Post subsidy realistic residential rooftop pricing
    "cost_per_kw_post_subsidy": (40000, 55000),

    "system_costs": {
        "1kw": (55000, 70000),

        "2kw": (95000, 125000),

        "3kw": (145000, 190000),

        "5kw": (240000, 320000),

        "10kw": (450000, 600000)
    },

    "cost_breakdown": {
        "panels": (0.50, 0.58),

        "inverter": (0.15, 0.20),

        "mounting": (0.10, 0.15),

        "balance_of_system": (0.10, 0.15)
    },

    "maintenance_cost_per_kw_per_year": (1000, 2500)
}


SUBSIDY_DATA = {
    "pm_surya_ghar": {
        "1_2kw": 30000,
        "additional_upto_3kw": 18000,
        "3kw_and_above": 78000
    }
}


INVERTER_DATA = {
    "efficiency": (0.96, 0.98),

    "cost_ranges": {
        "1kw": (10000, 18000),

        "3kw": (18000, 40000),

        "5kw": (35000, 70000)
    },

    "types": [
        "grid_tied",
        "off_grid",
        "hybrid",
        "microinverter",
        "string_inverter"
    ]
}


LOAD_PROFILE = {
    "daily_consumption_kwh": {

        # Average Hyderabad 1 AC family home
        "summer_ac_home": (10, 13),

        # Typical non-AC middle class home
        "non_ac_home": (4.5, 6.5)
    },

    "usage_split": {
        "day": 0.58,
        "night": 0.42
    },

    "appliance_share": {
        "ac": (0.35, 0.55),

        "others": (0.45, 0.65)
    }
}


APPLIANCE_DATA = {
    "ac": (1200, 1800),

    "refrigerator": (250, 450),

    "washing_machine": (150, 300),

    "induction_stove": (800, 1800),

    "geyser": (1000, 2000)
}


EV_DATA = {
    "car_kwh_per_km": (0.13, 0.18),

    "bike_kwh_per_km": (0.02, 0.04),

    "typical_values": {
        "car": 0.15,
        "bike": 0.03
    }
}


NET_METERING = {
    "capacity_limit_kw": (1, 1000),

    "settlement_cycle": ["June", "December"],

    "application_fee": 2500,

    "export_credit_type": "bill_credit"
}
