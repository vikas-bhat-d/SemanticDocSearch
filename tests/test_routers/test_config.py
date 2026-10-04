def test_get_settings(authenticated_client):
    res = authenticated_client.get("/api/config/settings")
    assert res.status_code == 200
    data = res.json()
    assert "embedding_model" in data
    assert data["conversion_timeout_seconds"] == 300.0
    assert data["qdrant_timeout_seconds"] == 30.0
    assert data["queue_put_timeout_seconds"] == 0.25
    assert data["worker_shutdown_timeout_seconds"] == 30.0


def test_timeout_settings_can_be_updated(authenticated_client):
    res = authenticated_client.put(
        "/api/config/settings",
        json={
            "conversion_timeout_seconds": 600,
            "qdrant_timeout_seconds": 45,
            "queue_put_timeout_seconds": 0.5,
            "worker_shutdown_timeout_seconds": 90,
        },
    )
    assert res.status_code == 200

    settings = authenticated_client.get("/api/config/settings")
    assert settings.status_code == 200
    data = settings.json()
    assert data["conversion_timeout_seconds"] == 600.0
    assert data["qdrant_timeout_seconds"] == 45.0
    assert data["queue_put_timeout_seconds"] == 0.5
    assert data["worker_shutdown_timeout_seconds"] == 90.0


def test_folders_crud(authenticated_client):
    # Add folder
    res = authenticated_client.post("/api/config/folders", json={"path": "C:\\TestFolder"})
    assert res.status_code == 200
    folder_id = res.json()["id"]

    # List folders
    res = authenticated_client.get("/api/config/folders")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Delete folder
    res = authenticated_client.delete(f"/api/config/folders/{folder_id}")
    assert res.status_code == 200


def test_exclusions_crud(authenticated_client):
    res = authenticated_client.post("/api/config/exclusions", json={"value": ".tmp", "type": "extension"})
    assert res.status_code == 200
    ex_id = res.json()["id"]

    res = authenticated_client.delete(f"/api/config/exclusions/{ex_id}")
    assert res.status_code == 200


def test_department_and_doc_type_updates(authenticated_client):
    department = authenticated_client.post(
        "/api/config/departments",
        json={"name": "Operations", "path_patterns": [r"*\Operations\*"]},
    )
    assert department.status_code == 200
    department_id = department.json()["id"]

    updated_department = authenticated_client.put(
        f"/api/config/departments/{department_id}",
        json={"name": "Operations & Support", "path_patterns": [r"*\Ops\*", r"*\Support\*"]},
    )
    assert updated_department.status_code == 200
    assert updated_department.json()["name"] == "Operations & Support"
    assert updated_department.json()["path_patterns"] == [r"*\Ops\*", r"*\Support\*"]

    doc_type = authenticated_client.post(
        "/api/config/doc-types",
        json={"name": "Procedure", "path_patterns": ["*procedure*"]},
    )
    assert doc_type.status_code == 200
    doc_type_id = doc_type.json()["id"]

    updated_doc_type = authenticated_client.put(
        f"/api/config/doc-types/{doc_type_id}",
        json={"name": "Standard Procedure", "path_patterns": ["*sop*", "*procedure*"]},
    )
    assert updated_doc_type.status_code == 200
    assert updated_doc_type.json()["name"] == "Standard Procedure"
    assert updated_doc_type.json()["path_patterns"] == ["*sop*", "*procedure*"]
