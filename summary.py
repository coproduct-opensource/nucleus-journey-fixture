"""Summarize ordinary CSV usage records by project and unit."""
import csv
import io
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, getcontext


def summarize_csv(text):
    # Set high precision for decimal operations to handle large numbers
    original_prec = getcontext().prec
    getcontext().prec = 50  # Support at least 30 significant decimal digits
    
    try:
        # Check for required columns
        lines = text.splitlines()
        if not lines:
            raise ValueError("columns")
        
        header = lines[0]
        columns = [col.strip() for col in header.split(",")]
        
        required_columns = {"project", "unit", "quantity"}
        if not required_columns.issubset(set(columns)):
            raise ValueError("columns")
        
        # Parse CSV data
        reader = csv.DictReader(io.StringIO(text))
        totals = {}
        
        for line_num, row in enumerate(reader, start=2):  # Start at 2 because header is line 1
            # Validate project and unit names
            project = row["project"].strip()
            unit = row["unit"].strip()
            
            if not project or not unit:
                raise ValueError(f"line {line_num}")
            
            # Normalize names
            project = project.strip()
            unit = unit.strip().lower()
            key = (project, unit)
            
            # Validate quantity
            quantity_str = row["quantity"].strip()
            if not quantity_str:
                raise ValueError(f"line {line_num}")
            
            try:
                quantity = Decimal(quantity_str)
            except InvalidOperation:
                raise ValueError(f"line {line_num}")
            
            if not quantity.is_finite():
                raise ValueError(f"line {line_num}")
            
            # Accumulate quantities
            if key in totals:
                totals[key] += quantity
            else:
                totals[key] = quantity
        
        # Format results with proper rounding and sorting
        result = []
        for (project, unit), quantity in sorted(totals.items()):
            # Round once per group to two decimal places using half-even rounding
            rounded_quantity = quantity.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
            
            # Format with exactly 2 decimal places
            result.append({
                "project": project,
                "unit": unit,
                "quantity": f"{rounded_quantity:.2f}"
            })
        
        return result
    finally:
        # Restore original precision
        getcontext().prec = original_prec
