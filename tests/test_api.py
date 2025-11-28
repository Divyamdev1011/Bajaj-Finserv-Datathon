from fastapi.testclient import TestClient
from src.api.main import app
def test_extract_missing():
    client = TestClient(app)
    r = client.post('/extract-bill-data')
    assert r.status_code == 422
