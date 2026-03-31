PARTS = {
    "Mk1 Command Pod": {"type": "pod", "mass": 840.0},
    "RT-5 Flea": {
        "type": "booster",
        "thrust": 163000.0,
        "fuel": 140.0,
        "burn_rate": 15.8,
        "dry_mass": 450.0,
        "fuel_mass": 1050.0,
    },
    "LV-T45 Swivel": {
        "type": "liquid_engine",
        "thrust": 168000.0,
        "fuel_rate": 13.7,
        "mass": 1500.0,
    },
    "FL-T100": {
        "type": "fuel_tank",
        "fuel": 100.0,
        "fuel_mass": 500.0,
        "dry_mass": 62.5,
    },
    "Mk16": {
        "type": "parachute",
        "semi_drag": 5.0,
        "full_drag": 500.0,
        "deploy_altitude": 1000.0,
    },
}


def build_vehicle(pod: str, engine: str, chute: str, tank: str | None = None) -> dict:
    return {
        "pod": PARTS[pod],
        "engine": PARTS[engine],
        "tank": PARTS[tank] if tank else None,
        "chute": PARTS[chute],
    }
