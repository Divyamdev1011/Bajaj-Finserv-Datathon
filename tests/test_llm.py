from src.extraction.llm_parser import parse_with_llm
def test_llm_fallback():
    sample = "Consultation 150\nMedicine 200\nTotal 350"
    res = parse_with_llm(sample)
    assert isinstance(res, list)
