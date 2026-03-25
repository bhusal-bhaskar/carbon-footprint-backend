def calculate_carbon_footprint(value, factor):
    try:
        # Automatic calculation to ensure data integrity
        return round(float(value) * float(factor), 2)
    except (ValueError, TypeError):
        return 0.0