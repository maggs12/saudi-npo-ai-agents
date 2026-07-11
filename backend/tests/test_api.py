from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_program():
    response = client.post("/api/v1/chat", json={"message": "قائمة البرامج"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "program"
    assert data["response"]


def test_chat_reporting():
    response = client.post("/api/v1/chat", json={"message": "تقرير PDF"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "reporting"
    assert data["response"]


def test_dashboard():
    response = client.get("/api/v1/dashboard?organization_id=1")
    assert response.status_code == 200
    data = response.json()
    assert "programs" in data
    assert "finance" in data


def test_generate_report():
    response = client.post(
        "/api/v1/reports",
        json={"report_type": "monthly", "period": "2026-01", "format": "pdf", "organization_id": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["file_path"].endswith(".pdf")

    # Download report
    report_id = data["report"]["id"]
    download = client.get(f"/api/v1/reports/{report_id}/download")
    assert download.status_code == 200
