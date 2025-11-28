"""
More advanced duplicate handling heuristics (stub).
"""
def dedupe_items(items):
    seen = {}
    result = []
    for it in items:
        key = (it['description'].strip().lower(), str(round(it.get('amount') or 0,2)))
        if key not in seen:
            seen[key] = True
            result.append(it)
    return result
