from unittest.mock import patch, MagicMock


def _make_mock_response(content):
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    return response


def _mock_create_course(client, name="博弈论基础"):
    syllabus_resp = _make_mock_response("# 测试课程 · 课程大纲\n\n## 核心掌握项\n\n### 模块一\n- [ ] 能够解释基本概念\n- [ ] 能够应用核心定理")
    lesson_resp = _make_mock_response("# 第一章\n\n正文内容\n\n## 思考题\n\n1. 问题一\n2. 问题二")

    with patch("app.courses.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [syllabus_resp, lesson_resp]
        mock_get_client.return_value = mock_client

        res = client.post("/api/courses", json={"name": name})
        assert res.status_code == 200
        return res.json()


def test_create_course(client):
    data = _mock_create_course(client)
    assert data["name"] == "博弈论基础"
    assert data["status"] == "learning"
    assert data["lesson_count"] == 1
    assert "课程大纲" in data["syllabus_content"]


def test_list_courses(client):
    _mock_create_course(client)
    res = client.get("/api/courses")
    assert res.status_code == 200
    courses = res.json()
    assert len(courses) == 1
    assert courses[0]["name"] == "博弈论基础"


def test_get_course_detail(client):
    data = _mock_create_course(client)
    res = client.get(f"/api/courses/{data['id']}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["name"] == "博弈论基础"
    assert "课程大纲" in detail["syllabus_content"]


def test_get_course_nonexistent(client):
    res = client.get("/api/courses/9999")
    assert res.status_code == 404


def test_get_syllabus(client):
    data = _mock_create_course(client)
    res = client.get(f"/api/courses/{data['id']}/syllabus")
    assert res.status_code == 200
    assert "课程大纲" in res.json()["content"]


def test_update_syllabus(client):
    data = _mock_create_course(client)
    new_content = "# 更新后的大纲\n\n- [x] 已掌握的内容"
    res = client.put(f"/api/courses/{data['id']}/syllabus", json={"content": new_content})
    assert res.status_code == 200
    assert res.json()["content"] == new_content


def test_list_lessons(client):
    data = _mock_create_course(client)
    res = client.get(f"/api/courses/{data['id']}/lessons")
    assert res.status_code == 200
    lessons = res.json()
    assert len(lessons) == 1
    assert lessons[0]["number"] == 1


def test_get_lesson(client):
    data = _mock_create_course(client)
    res = client.get(f"/api/courses/{data['id']}/lessons/1")
    assert res.status_code == 200
    assert "第一章" in res.json()["content"]


def test_get_lesson_nonexistent(client):
    data = _mock_create_course(client)
    res = client.get(f"/api/courses/{data['id']}/lessons/99")
    assert res.status_code == 404
