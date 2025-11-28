from src.totals.total_calculator import compute_totals
def test_total():
    items = [{'description':'A','amount':100.0},{'description':'B','amount':200.0}]
    res = compute_totals(items)
    assert res['calculated_total'] == 300.0
