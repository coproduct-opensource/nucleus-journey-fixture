"""Summarize ordinary CSV usage records by project and unit."""
import csv
import io
import decimal
from collections import defaultdict


def summarize_csv(text):
    # Configure decimal for exact arithmetic with proper rounding
    decimal.getcontext().prec = 30
    decimal.getcontext().rounding = decimal.ROUND_HALF_EVEN
    
    # Parse CSV and validate columns
    reader = csv.DictReader(io.StringIO(text))
    required_columns = {"project", "unit", "quantity"}
    missing_columns = required_columns - set(reader.fieldnames)
    if missing_columns:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing_columns))}")
    
    totals = defaultdict(decimal.Decimal)
    line_number = 1  # Header is line 1
    
    # Process each row
    for row in reader:
        line_number = reader.line_num
        project = row["project"].strip()
        unit = row["unit"].strip().lower()
        quantity_str = row["quantity"]
        
        # Validate names
        if not project:
            raise ValueError(f"Empty project name on line {line_number}")
        if not unit:
            raise ValueError(f"Empty unit name on line {line_number}")
        
        # Validate quantity
        try:
            quantity = decimal.Decimal(quantity_str)
        except (decimal.InvalidOperation, TypeError):
            raise ValueError(f"Invalid quantity on line {line_number}")
        
        if not quantity.is_finite():
            raise ValueError(f"Non-finite quantity on line {line_number}")
        
        # Accumulate with exact arithmetic
        key = (project, unit)
        totals[key] += quantity
    
    # Format results
    result = []
    for (project, unit), quantity in sorted(totals.items()):
        # Round once per group to two decimal places
        rounded = quantity.quantize(decimal.Decimal('0.01'))
        result.append({
            "project": project,
            "unit": unit,
            "quantity": f"{rounded:.2f}"
        })
    
    return result
