try:
    from fastapi.testclient import TestClient
except Exception:  # pragma: no cover - fastapi not available in minimal env
    import pytest

    pytest.skip(
        "fastapi/TestClient not available in this environment", allow_module_level=True
    )

from app.main import app


client = TestClient(app)


def test_score_endpoint_basic():
    sample = "Hello, I am Tanishq. I like coding, music and sports. I have worked on projects."
    resp = client.post("/score", json={"text": sample})
    assert resp.status_code == 200
    data = resp.json()
    # Basic contract
    assert isinstance(data, dict)
    assert "overall_score" in data
    assert "word_count" in data
    assert "criteria" in data
    assert isinstance(data.get("criteria"), list)
