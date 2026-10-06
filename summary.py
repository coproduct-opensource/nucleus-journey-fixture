"""Summarize ordinary CSV usage records by project and unit."""
import csv
import io
import decimal
from collections import defaultdict


def summarize_csv(text):
    # Use Decimal for exact arithmetic
    decimal.getcontext().prec = 30
    
    # Parse CSV
    reader = csv.DictReader(io.StringIO(text))
    fieldnames = reader.fieldnames or []
    
    # Check required columns
    required = {"project", "unit", "quantity"}
    missing = required - set(fieldnames)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    
    # Process rows
    totals = defaultdict(decimal.Decimal)
    line_number = 1  # Header is line 1
    
    for row in reader:
        line_number = reader.line_num
        
        # Get and validate fields
        project = row["project"].strip()
        unit = row["unit"].strip().lower()
        quantity_str = row["quantity"].strip()
        
        # Check for empty names
        if not project:
            raise ValueError(f"Empty project name on line {line_number}")
        if not unit:
            raise ValueError(f"Empty unit name on line {line_number}")
        
        # Validate quantity
        try:
            quantity = decimal.Decimal(quantity_str)
        except (decimal.InvalidOperation, ValueError):
            raise ValueError(f"Invalid quantity on line {line_number}")
        
        if not quantity.is_finite():
            raise ValueError(f"Non-finite quantity on line {line_number}")
        
        # Accumulate
        key = (project, unit)
        totals[key] += quantity
    
    # Format results
    result = []
    for (project, unit), quantity in sorted(totals.items()):
        # Round once per group using half-even rounding
        rounded = quantity.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_EVEN)
        result.append({
            "project": project,
            "unit": unit,
            "quantity": f"{rounded:.2f}"
        })
    
    return result
