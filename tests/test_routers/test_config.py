from datetime import datetime, timedelta

from app.models import FolderDeleteChallenge, IndexFolder, IndexRun


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


def test_folders_crud(authenticated_client, mock_qdrant):
    # Add folder
    res = authenticated_client.post("/api/config/folders", json={"path": "C:\\TestFolder"})
    assert res.status_code == 200
    folder_id = res.json()["id"]

    # List folders
    res = authenticated_client.get("/api/config/folders")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Request and submit the destructive deletion challenge
    challenge = authenticated_client.post(
        f"/api/config/folders/{folder_id}/delete-challenge"
    )
    assert challenge.status_code == 200
    challenge_data = challenge.json()
    assert len(challenge_data["code"]) == 6
    assert challenge_data["code"].isdigit()

    # Delete folder and its Qdrant points
    res = authenticated_client.request(
        "DELETE",
        f"/api/config/folders/{folder_id}",
        json={
            "challenge_id": challenge_data["challenge_id"],
            "code": challenge_data["code"],
        },
    )
    assert res.status_code == 200


def test_folder_delete_rejects_incorrect_code(authenticated_client, mock_qdrant):
    created = authenticated_client.post(
        "/api/config/folders",
        json={"path": r"C:\WrongCodeFolder"},
    )
    folder_id = created.json()["id"]
    challenge = authenticated_client.post(
        f"/api/config/folders/{folder_id}/delete-challenge"
    )
    challenge_data = challenge.json()

    response = authenticated_client.request(
        "DELETE",
        f"/api/config/folders/{folder_id}",
        json={
            "challenge_id": challenge_data["challenge_id"],
            "code": "000000" if challenge_data["code"] != "000000" else "999999",
        },
    )

    assert response.status_code == 400
    assert any(
        folder["id"] == folder_id
        for folder in authenticated_client.get("/api/config/folders").json()
    )


def test_folder_delete_rejects_expired_challenge(
    authenticated_client,
    db_session,
):
    created = authenticated_client.post(
        "/api/config/folders",
        json={"path": r"C:\ExpiredChallengeFolder"},
    )
    folder_id = created.json()["id"]
    challenge = authenticated_client.post(
        f"/api/config/folders/{folder_id}/delete-challenge"
    )
    challenge_data = challenge.json()
    row = db_session.get(FolderDeleteChallenge, challenge_data["challenge_id"])
    row.expires_at = datetime.utcnow() - timedelta(seconds=1)
    db_session.commit()

    response = authenticated_client.request(
        "DELETE",
        f"/api/config/folders/{folder_id}",
        json={
            "challenge_id": challenge_data["challenge_id"],
            "code": challenge_data["code"],
        },
    )

    assert response.status_code == 409
    assert db_session.get(IndexFolder, folder_id) is not None


def test_folder_delete_qdrant_failure_preserves_folder(
    authenticated_client,
    mock_qdrant,
    db_session,
):
    created = authenticated_client.post(
        "/api/config/folders",
        json={"path": r"C:\QdrantFailureFolder"},
    )
    folder_id = created.json()["id"]
    challenge = authenticated_client.post(
        f"/api/config/folders/{folder_id}/delete-challenge"
    )
    challenge_data = challenge.json()
    mock_qdrant.delete.side_effect = RuntimeError("qdrant unavailable")
    mock_qdrant.scroll.side_effect = RuntimeError("qdrant unavailable")

    response = authenticated_client.request(
        "DELETE",
        f"/api/config/folders/{folder_id}",
        json={
            "challenge_id": challenge_data["challenge_id"],
            "code": challenge_data["code"],
        },
    )

    assert response.status_code == 502
    assert db_session.get(IndexFolder, folder_id) is not None


def test_folder_delete_challenge_is_blocked_during_active_run(
    authenticated_client,
    db_session,
):
    created = authenticated_client.post(
        "/api/config/folders",
        json={"path": r"C:\ActiveRunFolder"},
    )
    folder_id = created.json()["id"]
    db_session.add(IndexRun(status="running"))
    db_session.commit()

    response = authenticated_client.post(
        f"/api/config/folders/{folder_id}/delete-challenge"
    )

    assert response.status_code == 409


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
