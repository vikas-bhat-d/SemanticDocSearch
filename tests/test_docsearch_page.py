def test_docsearch_page_is_standalone(client):
    response = client.get("/DocSearch.html")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    body = response.text
    assert "Search documents" in body
    assert "department" in body
    assert "doc_type" in body
    assert "extension" in body
    assert "per_page" in body
    assert "safeExcerpt" in body


def test_folder_page_exposes_delete_progress_overlay(authenticated_client):
    response = authenticated_client.get("/folders")

    assert response.status_code == 200
    assert "folder-delete-overlay" in response.text
    assert 'id="folder-delete-overlay" class="operation-overlay" hidden' in response.text
    assert "Removing matching Qdrant points" in response.text
    assert "folder-delete-close" in response.text

    styles = authenticated_client.get("/static/css/app.css")
    assert styles.status_code == 200
    assert ".operation-overlay[hidden]" in styles.text
    assert "#folder-delete-close[hidden]" in styles.text
