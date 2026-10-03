def test_incremental_config_crud(authenticated_client):
    res = authenticated_client.post("/api/incremental/config", json={
        "changed_xml_path": "C:\\changed.xml",
        "deleted_xml_path": "C:\\deleted.xml"
    })
    assert res.status_code == 200

    res = authenticated_client.get("/api/incremental/config")
    assert res.status_code == 200
    data = res.json()
    assert data["changed_xml_path"] == "C:\\changed.xml"
