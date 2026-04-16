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
            "efficiency": (0.18, 0.22),
            "cost_per_watt": (40, 60),
            "typical_wattage": (400, 550)
        },
        "polycrystalline": {
            "efficiency": (0.15, 0.17),
            "cost_per_watt": (30, 50),
            "typical_wattage": (300, 400)
        },
        "bifacial": {
            "efficiency": (0.18, 0.24),
            "cost_per_watt": (50, 70),
            "typical_wattage": (500, 600)
        }
    },

    "panel_dimensions": {
        "standard_area_m2": 2.0,
        "large_panel_area_m2": 2.4
    },

    "panels_per_kw": (6, 8),

    "space_required_per_kw_sqft": (100, 120),

    "tilt_angle_optimal": (12, 19),

    "orientation_factor": {
        "south": 1.0,
        "east_west": 0.85,
        "north": 0.7
    }
}

LOSS_FACTORS = {
    "temperature_loss": (0.10, 0.15),
    "dust_loss": (0.05, 0.25),
    "inverter_loss": (0.03, 0.07),
    "dc_loss": (0.01, 0.03),
    "mismatch_loss": (0.01, 0.02),
    "reflection_loss": (0.02, 0.04),

    "total_system_loss": (0.15, 0.25),

    "performance_ratio": (0.75, 0.85),

    "degradation": {
        "initial": 0.025,
        "annual": (0.005, 0.007)
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

    "export_rate_factor": (0.5, 0.6),  # 50–60% of tariff

    "electricity_inflation": (0.03, 0.05)
}

MONTHLY_CONSUMPTION_FACTORS = {
    "Jan": 0.9,
    "Feb": 0.9,
    "Mar": 1.1,
    "Apr": 1.3,
    "May": 1.4,
    "Jun": 1.2,
    "Jul": 1.0,
    "Aug": 1.0,
    "Sep": 1.0,
    "Oct": 0.9,
    "Nov": 0.9,
    "Dec": 0.9
}

FINANCIAL_DATA = {
    "cost_per_kw_post_subsidy": (40000, 60000),

    "system_costs": {
        "1kw": (50000, 60000),
        "2kw": 105000,
        "3kw": (110000, 130000),
        "5kw": 365000,
        "10kw": 492000
    },

    "cost_breakdown": {
        "panels": (0.50, 0.60),
        "inverter": (0.15, 0.20),
        "mounting": (0.10, 0.15),
        "balance_of_system": (0.10, 0.15)
    },

    "maintenance_cost_per_kw_per_year": (1000, 3000)
}

SUBSIDY_DATA = {
    "pm_surya_ghar": {
        "1_2kw": 30000,
        "additional_upto_3kw": 18000,
        "3kw_and_above": 78000
    }
}

INVERTER_DATA = {
    "efficiency": (0.95, 0.98),

    "cost_ranges": {
        "1kw": (8000, 20000),
        "3kw": (20000, 50000),
        "5kw": (40000, 80000)
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
        "summer_ac_home": 15.1,
        "non_ac_home": (6.1, 6.6)
    },

    "usage_split": {
        "day": 0.6,
        "night": 0.4
    },

    "appliance_share": {
        "ac": (0.39, 0.65),
        "others": (0.35, 0.61)
    }
}

APPLIANCE_DATA = {
    "ac": (1200, 2000),
    "refrigerator": (300, 500),
    "washing_machine": (150, 300),
    "induction_stove": (500, 800),
    "geyser": (800, 1500)
}

EV_DATA = {
    "car_kwh_per_km": (0.13, 0.20),
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
