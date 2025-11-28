"""
Validators to compare calculated totals with reported totals and flag mismatches.
"""
def validate_totals(calculated: float, reported: float, tolerance_percent: float = 1.0):
    diff = abs(calculated - reported)
    if reported == 0:
        return {'matches': calculated == 0, 'diff': diff, 'percent': None}
    percent = (diff / reported) * 100.0
    return {'matches': percent <= tolerance_percent, 'diff': diff, 'percent': percent}
