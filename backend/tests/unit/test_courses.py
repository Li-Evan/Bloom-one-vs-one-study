from unittest.mock import patch, MagicMock


def _make_mock_response(content):
    """Create a mock OpenAI non-streaming response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    return response


def _mock_create_course(auth_client, name="博弈论基础"):
    """Helper to create a course with mocked LLM."""
    syllabus_resp = _make_mock_response("# 测试课程 · 课程大纲\n\n## 核心掌握项\n\n### 模块一\n- [ ] 能够解释基本概念\n- [ ] 能够应用核心定理")
    lesson_resp = _make_mock_response("# 第一章\n\n正文内容\n\n## 思考题\n\n1. 问题一\n2. 问题二")

    with patch("app.courses.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [syllabus_resp, lesson_resp]
        mock_get_client.return_value = mock_client

        res = auth_client.post("/api/courses", json={"name": name})
        assert res.status_code == 200
        return res.json()


def test_create_course(auth_client):
    data = _mock_create_course(auth_client)
    assert data["name"] == "博弈论基础"
    assert data["status"] == "learning"
    assert data["lesson_count"] == 1
    assert "课程大纲" in data["syllabus_content"]

    # Verify credit deducted
    balance = auth_client.get("/api/credits/balance").json()
    assert balance["credits"] == 99


def test_list_courses(auth_client):
    _mock_create_course(auth_client)

    res = auth_client.get("/api/courses")
    assert res.status_code == 200
    courses = res.json()
    assert len(courses) == 1
    assert courses[0]["name"] == "博弈论基础"
    assert courses[0]["status"] == "learning"
    assert courses[0]["lesson_count"] == 1


def test_get_course_detail(auth_client):
    data = _mock_create_course(auth_client)
    course_id = data["id"]

    res = auth_client.get(f"/api/courses/{course_id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["name"] == "博弈论基础"
    assert detail["syllabus_content"] is not None
    assert "课程大纲" in detail["syllabus_content"]


def test_get_course_nonexistent(auth_client):
    res = auth_client.get("/api/courses/9999")
    assert res.status_code == 404


def test_courses_no_auth(client):
    res = client.get("/api/courses")
    assert res.status_code in (401, 403)


def test_get_syllabus(auth_client):
    data = _mock_create_course(auth_client)
    course_id = data["id"]

    res = auth_client.get(f"/api/courses/{course_id}/syllabus")
    assert res.status_code == 200
    syllabus = res.json()
    assert "课程大纲" in syllabus["content"]


def test_update_syllabus(auth_client):
    data = _mock_create_course(auth_client)
    course_id = data["id"]

    new_content = "# 更新后的大纲\n\n- [x] 已掌握的内容"
    res = auth_client.put(f"/api/courses/{course_id}/syllabus", json={"content": new_content})
    assert res.status_code == 200
    assert res.json()["content"] == new_content


def test_list_lessons(auth_client):
    data = _mock_create_course(auth_client)
    course_id = data["id"]

    res = auth_client.get(f"/api/courses/{course_id}/lessons")
    assert res.status_code == 200
    lessons = res.json()
    assert len(lessons) == 1
    assert lessons[0]["number"] == 1
    assert lessons[0]["is_evaluation"] is False


def test_get_lesson(auth_client):
    data = _mock_create_course(auth_client)
    course_id = data["id"]

    res = auth_client.get(f"/api/courses/{course_id}/lessons/1")
    assert res.status_code == 200
    lesson = res.json()
    assert lesson["number"] == 1
    assert "第一章" in lesson["content"]


def test_get_lesson_nonexistent(auth_client):
    data = _mock_create_course(auth_client)
    course_id = data["id"]

    res = auth_client.get(f"/api/courses/{course_id}/lessons/99")
    assert res.status_code == 404


def test_create_course_insufficient_credits(auth_client):
    """Drain credits then try to create course."""
    from sqlalchemy import update
    from app.models import User
    import app.database as app_database

    with app_database.SessionLocal() as db:
        db.execute(update(User).values(credits=0))
        db.commit()

    res = auth_client.post("/api/courses", json={"name": "应该失败"})
    assert res.status_code == 402
