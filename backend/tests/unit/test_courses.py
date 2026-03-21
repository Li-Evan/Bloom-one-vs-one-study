def test_create_course(auth_client):
    res = auth_client.post("/api/courses", json={"name": "博弈论基础"})
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "博弈论基础"
    assert data["message_count"] == 0


def test_list_courses(auth_client):
    auth_client.post("/api/courses", json={"name": "课程1"})
    auth_client.post("/api/courses", json={"name": "课程2"})
    res = auth_client.get("/api/courses")
    assert res.status_code == 200
    courses = res.json()
    assert len(courses) == 2


def test_get_messages_empty(auth_client):
    course = auth_client.post("/api/courses", json={"name": "测试课程"}).json()
    res = auth_client.get(f"/api/courses/{course['id']}/messages")
    assert res.status_code == 200
    assert res.json() == []


def test_get_messages_nonexistent_course(auth_client):
    res = auth_client.get("/api/courses/9999/messages")
    assert res.status_code == 404


def test_courses_no_auth(client):
    res = client.get("/api/courses")
    assert res.status_code in (401, 403)
