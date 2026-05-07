import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_fence_analysis_mock():
    payload = {
        "fence_geojson": {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [114.935, 25.831],
                        [114.945, 25.831],
                        [114.945, 25.841],
                        [114.935, 25.841],
                        [114.935, 25.831],
                    ]
                ],
            },
            "properties": {"name": "用户圈定宅基地范围"},
        },
        "analysis_mode": "environment",
        "use_mock": True,
    }
    response = client.post("/api/analysis/fence", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["fence_info"]["area_m2"] > 0
    assert data["scores"]["overall_score"] > 0
    assert "免责声明" in data["report"]
