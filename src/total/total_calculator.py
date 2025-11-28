"""
Compute totals from parsed line items; handle duplicates and rounding.
"""
def compute_totals(items):
    cleaned = [it for it in items if it.get('amount') is not None]
    seen = set()
    unique = []
    for it in cleaned:
        key = (it['description'].strip().lower(), float(it['amount']))
        if key not in seen:
            seen.add(key)
            unique.append({'description': it['description'], 'amount': float(it['amount'])})
    total = sum(it['amount'] for it in unique)
    return {'line_items': unique, 'calculated_total': round(total, 2)}
