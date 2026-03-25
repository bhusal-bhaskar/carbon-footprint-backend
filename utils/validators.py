def validate_activity_data(data):
    """
    Validates activity input and ensures numeric integrity.
    """
    errors = []
    
    # Check for required top-level fields [cite: 27-36]
    required_fields = ['activity_type', 'activity_value', 'emission_factor', 'unit']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Type and Range Checking 
    try:
        if float(data.get('activity_value', 0)) <= 0:
            errors.append("activity_value must be a positive number.")
        if float(data.get('emission_factor', 0)) < 0:
            errors.append("emission_factor cannot be negative.")
    except (ValueError, TypeError):
        errors.append("activity_value and emission_factor must be numeric.")

    # Validate activity_type against allowed categories [cite: 66]
    allowed_types = ['Transport', 'Energy', 'Consumption']
    if data.get('activity_type') not in allowed_types:
        errors.append(f"Invalid activity_type. Must be one of: {', '.join(allowed_types)}")

    return errors