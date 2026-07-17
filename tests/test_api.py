import json
from pathlib import Path

from fastapi.testclient import TestClient

from resume_matching_agent.api.main import MAX_FILE_BYTES, app


client = TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Resume upload – happy path
# ---------------------------------------------------------------------------


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


def test_resume_upload_response_contains_required_fields(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))

    response = client.post(
        "/api/v1/intake/resumes/upload",
        files={"file": ("cv.txt", b"skill: python", "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "resumeId" in payload
    assert "status" in payload
    assert "storedAtUtc" in payload


def test_resume_upload_writes_metadata_json(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))

    response = client.post(
        "/api/v1/intake/resumes/upload",
        files={"file": ("my_resume.txt", b"experience: 5 years", "text/plain")},
    )

    assert response.status_code == 200
    resume_id = response.json()["resumeId"]

    meta_path = tmp_path / "intake" / "resumes" / f"{resume_id}.json"
    assert meta_path.exists()

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["id"] == resume_id
    assert meta["kind"] == "resumes"
    assert meta["originalFileName"] == "my_resume.txt"
    assert meta["status"] == "Ready for processing"
    assert "storedAtUtc" in meta


def test_resume_upload_persists_file_content(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))
    content = "python, fastapi, azure"

    response = client.post(
        "/api/v1/intake/resumes/upload",
        files={"file": ("resume.txt", content.encode("utf-8"), "text/plain")},
    )

    assert response.status_code == 200
    resume_id = response.json()["resumeId"]

    txt_path = tmp_path / "intake" / "resumes" / f"{resume_id}.txt"
    assert txt_path.read_text(encoding="utf-8") == content


# ---------------------------------------------------------------------------
# Resume upload – validation errors
# ---------------------------------------------------------------------------


def test_resume_upload_rejects_non_txt_extension(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))

    response = client.post(
        "/api/v1/intake/resumes/upload",
        files={"file": ("resume.pdf", b"some content", "application/pdf")},
    )

    assert response.status_code == 400
    assert "Only .txt files are allowed" in response.text


def test_resume_upload_rejects_docx_extension(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))

    response = client.post(
        "/api/v1/intake/resumes/upload",
        files={"file": ("resume.docx", b"word doc bytes", "application/vnd.openxmlformats-officedocument")},
    )

    assert response.status_code == 400
    assert "Only .txt files are allowed" in response.text


def test_resume_upload_rejects_oversize_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))
    oversize_payload = b"a" * (MAX_FILE_BYTES + 1)

    response = client.post(
        "/api/v1/intake/resumes/upload",
        files={"file": ("big.txt", oversize_payload, "text/plain")},
    )

    assert response.status_code == 400
    assert "File size exceeds 1 MB" in response.text


def test_resume_upload_rejects_non_utf8_encoding(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))
    latin1_bytes = "café résumé".encode("latin-1")

    response = client.post(
        "/api/v1/intake/resumes/upload",
        files={"file": ("resume.txt", latin1_bytes, "text/plain")},
    )

    assert response.status_code == 400
    assert "File must be UTF-8 encoded" in response.text


def test_resume_upload_accepts_exactly_1mb_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))
    exact_payload = b"x" * MAX_FILE_BYTES

    response = client.post(
        "/api/v1/intake/resumes/upload",
        files={"file": ("exact.txt", exact_payload, "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Ready for processing"


# ---------------------------------------------------------------------------
# Requirement upload – happy path
# ---------------------------------------------------------------------------


def test_requirement_upload_persists_utf8_txt(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))

    response = client.post(
        "/api/v1/intake/requirements/upload",
        files={"file": ("req.txt", b"senior python developer", "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "Ready for matching"

    saved = tmp_path / "intake" / "requirements" / f"{payload['requirementId']}.txt"
    assert saved.exists()


def test_requirement_upload_response_contains_required_fields(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))

    response = client.post(
        "/api/v1/intake/requirements/upload",
        files={"file": ("req.txt", b"need azure skills", "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "requirementId" in payload
    assert "status" in payload
    assert "storedAtUtc" in payload


def test_requirement_upload_writes_metadata_json(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))

    response = client.post(
        "/api/v1/intake/requirements/upload",
        files={"file": ("project_req.txt", b"fastapi, azure, python", "text/plain")},
    )

    assert response.status_code == 200
    requirement_id = response.json()["requirementId"]

    meta_path = tmp_path / "intake" / "requirements" / f"{requirement_id}.json"
    assert meta_path.exists()

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["id"] == requirement_id
    assert meta["kind"] == "requirements"
    assert meta["originalFileName"] == "project_req.txt"
    assert meta["status"] == "Ready for matching"
    assert "storedAtUtc" in meta


def test_requirement_upload_persists_file_content(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))
    content = "5 years python, azure devops experience required"

    response = client.post(
        "/api/v1/intake/requirements/upload",
        files={"file": ("req.txt", content.encode("utf-8"), "text/plain")},
    )

    assert response.status_code == 200
    requirement_id = response.json()["requirementId"]

    txt_path = tmp_path / "intake" / "requirements" / f"{requirement_id}.txt"
    assert txt_path.read_text(encoding="utf-8") == content


# ---------------------------------------------------------------------------
# Requirement upload – validation errors
# ---------------------------------------------------------------------------


def test_requirement_upload_rejects_non_txt_extension(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))

    response = client.post(
        "/api/v1/intake/requirements/upload",
        files={"file": ("req.pdf", b"not txt", "application/pdf")},
    )

    assert response.status_code == 400
    assert "Only .txt files are allowed" in response.text


def test_requirement_upload_rejects_oversize_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))
    oversize_payload = b"b" * (MAX_FILE_BYTES + 1)

    response = client.post(
        "/api/v1/intake/requirements/upload",
        files={"file": ("big_req.txt", oversize_payload, "text/plain")},
    )

    assert response.status_code == 400
    assert "File size exceeds 1 MB" in response.text


def test_requirement_upload_rejects_non_utf8_encoding(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))
    latin1_bytes = "senior développeur".encode("latin-1")

    response = client.post(
        "/api/v1/intake/requirements/upload",
        files={"file": ("req.txt", latin1_bytes, "text/plain")},
    )

    assert response.status_code == 400
    assert "File must be UTF-8 encoded" in response.text


def test_requirement_upload_accepts_exactly_1mb_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RMA_STORAGE_ROOT", str(tmp_path))
    exact_payload = b"y" * MAX_FILE_BYTES

    response = client.post(
        "/api/v1/intake/requirements/upload",
        files={"file": ("exact_req.txt", exact_payload, "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Ready for matching"
