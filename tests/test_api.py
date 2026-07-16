from pathlib import Path

from fastapi.testclient import TestClient

from resume_matching_agent.api.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_resume_upload_persists_utf8_txt(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))

    response = client.post(
        "/api/v1/intake/resumes/upload",
        files={"file": ("resume.txt", b"python, fastapi", "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "Ready for processing"

    saved = tmp_path / "intake" / "resumes" / f"{payload['resumeId']}.txt"
    assert saved.exists()


def test_requirement_upload_rejects_non_txt_extension(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))

    response = client.post(
        "/api/v1/intake/requirements/upload",
        files={"file": ("req.pdf", b"not txt", "application/pdf")},
    )

    assert response.status_code == 400
    assert "Only .txt files are allowed" in response.text
