def test_get_settings(authenticated_client):
    res = authenticated_client.get("/api/config/settings")
    assert res.status_code == 200
    data = res.json()
    assert "embedding_model" in data


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
