def test_reclassify_endpoint(authenticated_client, mock_qdrant):
    res = authenticated_client.post("/api/reclassify", json={
        "file_path": "\\\\pc135\\D\\HR\\policy.docx",
        "departments": ["HR", "Legal"],
        "doc_types": ["CL"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
