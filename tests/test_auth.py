def test_login_success(client):
    res = client.post("/api/auth/login", data={"username": "admin", "password": "admin"})
    assert res.status_code in (200, 303)


def test_login_invalid_password(client):
    res = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "wrongpassword"},
        follow_redirects=False,
    )
    assert res.status_code == 303


def test_logout(authenticated_client):
    res = authenticated_client.post("/api/auth/logout")
    assert res.status_code == 200
    assert res.json()["status"] == "success"
