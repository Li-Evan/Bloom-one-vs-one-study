def test_register(client):
    res = client.post("/api/auth/register", json={
        "email": "new@example.com",
        "username": "newuser",
        "password": "password123",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "username": "user1",
        "password": "password123",
    })
    res = client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "username": "user2",
        "password": "password123",
    })
    assert res.status_code == 400
    assert "已注册" in res.json()["detail"]


def test_register_duplicate_username(client):
    client.post("/api/auth/register", json={
        "email": "a@example.com",
        "username": "sameuser",
        "password": "password123",
    })
    res = client.post("/api/auth/register", json={
        "email": "b@example.com",
        "username": "sameuser",
        "password": "password123",
    })
    assert res.status_code == 400
    assert "已被使用" in res.json()["detail"]


def test_login_success(client):
    client.post("/api/auth/register", json={
        "email": "login@example.com",
        "username": "loginuser",
        "password": "password123",
    })
    res = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "password123",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "email": "wrong@example.com",
        "username": "wronguser",
        "password": "password123",
    })
    res = client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpassword",
    })
    assert res.status_code == 401
    assert "密码错误" in res.json()["detail"]


def test_me(auth_client):
    res = auth_client.get("/api/auth/me")
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["credits"] == 100


def test_register_invalid_username(client):
    res = client.post("/api/auth/register", json={
        "email": "baduser@example.com",
        "username": "<script>alert(1)</script>",
        "password": "password123",
    })
    assert res.status_code == 422


def test_register_short_password(client):
    res = client.post("/api/auth/register", json={
        "email": "short@example.com",
        "username": "shortpwuser",
        "password": "12345",
    })
    assert res.status_code == 422


def test_me_no_auth(client):
    res = client.get("/api/auth/me")
    assert res.status_code in (401, 403)
