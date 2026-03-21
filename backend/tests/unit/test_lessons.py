from unittest.mock import patch, MagicMock


def _make_mock_response(content):
    """Create a mock OpenAI non-streaming response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    return response


def _make_mock_stream(content_chunks):
    """Create a mock OpenAI streaming response."""
    chunks = []
    for text in content_chunks:
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = text
        chunks.append(chunk)
    final = MagicMock()
    final.choices = [MagicMock()]
    final.choices[0].delta.content = None
    chunks.append(final)
    return iter(chunks)


def _setup_course(auth_client, syllabus_content=None):
    """Create a course with mocked LLM, return course_id."""
    if syllabus_content is None:
        syllabus_content = "# 测试 · 课程大纲\n\n## 核心掌握项\n\n### 模块一\n- [ ] 能够解释概念"
    syllabus_resp = _make_mock_response(syllabus_content)
    lesson_resp = _make_mock_response("# 第一章\n\n正文\n\n## 思考题\n\n1. 问题")

    with patch("app.courses.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [syllabus_resp, lesson_resp]
        mock_get_client.return_value = mock_client
        data = auth_client.post("/api/courses", json={"name": "测试课程"}).json()

    return data["id"]


# --- Annotation Tests ---

def test_create_annotation(auth_client):
    course_id = _setup_course(auth_client)

    res = auth_client.post(f"/api/courses/{course_id}/lessons/1/annotations", json={
        "position_start": 10,
        "position_end": 20,
        "original_text": "正文",
        "comment": "这里不太理解",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["original_text"] == "正文"
    assert data["comment"] == "这里不太理解"
    assert data["position_start"] == 10
    assert data["position_end"] == 20


def test_get_annotations(auth_client):
    course_id = _setup_course(auth_client)

    auth_client.post(f"/api/courses/{course_id}/lessons/1/annotations", json={
        "position_start": 0, "position_end": 5, "original_text": "文本1", "comment": "???为什么",
    })
    auth_client.post(f"/api/courses/{course_id}/lessons/1/annotations", json={
        "position_start": 10, "position_end": 15, "original_text": "文本2", "comment": "???不懂",
    })

    res = auth_client.get(f"/api/courses/{course_id}/lessons/1/annotations")
    assert res.status_code == 200
    annotations = res.json()
    assert len(annotations) == 2


def test_annotation_nonexistent_lesson(auth_client):
    course_id = _setup_course(auth_client)
    res = auth_client.post(f"/api/courses/{course_id}/lessons/99/annotations", json={
        "position_start": 0, "position_end": 5, "original_text": "text", "comment": "comment",
    })
    assert res.status_code == 404


def test_annotation_invalid_positions(auth_client):
    """position_end < position_start should be rejected."""
    course_id = _setup_course(auth_client)
    res = auth_client.post(f"/api/courses/{course_id}/lessons/1/annotations", json={
        "position_start": 20,
        "position_end": 5,
        "original_text": "text",
        "comment": "comment",
    })
    assert res.status_code == 422


# --- Feedback Tests ---

def test_create_feedback(auth_client):
    course_id = _setup_course(auth_client)

    res = auth_client.post(f"/api/courses/{course_id}/lessons/1/feedback", json={
        "content": "这一章讲得很好，但第二个概念还是不太清楚",
        "thought_answers": '{"q1": "我的答案是..."}',
    })
    assert res.status_code == 200
    data = res.json()
    assert "不太清楚" in data["content"]


def test_update_feedback(auth_client):
    """Submitting feedback twice should update, not duplicate."""
    course_id = _setup_course(auth_client)

    auth_client.post(f"/api/courses/{course_id}/lessons/1/feedback", json={
        "content": "初始反馈",
        "thought_answers": "",
    })
    res = auth_client.post(f"/api/courses/{course_id}/lessons/1/feedback", json={
        "content": "更新后的反馈",
        "thought_answers": '{"q1": "更新答案"}',
    })
    assert res.status_code == 200
    assert res.json()["content"] == "更新后的反馈"


def test_feedback_nonexistent_lesson(auth_client):
    course_id = _setup_course(auth_client)
    res = auth_client.post(f"/api/courses/{course_id}/lessons/99/feedback", json={
        "content": "test", "thought_answers": "",
    })
    assert res.status_code == 404


def test_feedback_plain_text_thought_answers(auth_client):
    """thought_answers accepts plain text (not just JSON)."""
    course_id = _setup_course(auth_client)
    res = auth_client.post(f"/api/courses/{course_id}/lessons/1/feedback", json={
        "content": "反馈",
        "thought_answers": "第1题：我觉得答案是X\n第2题：答案是Y",
    })
    assert res.status_code == 200


# --- Generate Next Lesson Tests ---

def test_generate_next_lesson(auth_client):
    course_id = _setup_course(auth_client)

    # Submit feedback first
    auth_client.post(f"/api/courses/{course_id}/lessons/1/feedback", json={
        "content": "我理解了基本概念",
        "thought_answers": '{"q1": "答案"}',
    })

    next_stream = _make_mock_stream(["# 第二章\n\n## 上一篇思考题复盘\n\n✅ 正确\n\n## 正文\n\n新内容"])

    with patch("app.courses.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = next_stream
        mock_get_client.return_value = mock_client

        res = auth_client.post(f"/api/courses/{course_id}/next")
        assert res.status_code == 200
        assert "text/event-stream" in res.headers["content-type"]
        body = res.text
        assert '"done": true' in body

    # Verify new lesson exists
    lessons = auth_client.get(f"/api/courses/{course_id}/lessons").json()
    assert len(lessons) == 2
    assert lessons[1]["number"] == 2


def test_generate_next_no_auth(client):
    res = client.post("/api/courses/1/next")
    assert res.status_code in (401, 403)


def test_generate_next_completed_course(auth_client):
    course_id = _setup_course(auth_client)

    from sqlalchemy import update
    from app.models import Course
    import app.database as app_database
    with app_database.SessionLocal() as db:
        db.execute(update(Course).where(Course.id == course_id).values(status="completed"))
        db.commit()

    res = auth_client.post(f"/api/courses/{course_id}/next")
    assert res.status_code == 400
    assert "已完结" in res.json()["detail"]


def test_generate_eval_when_all_mastery_done(auth_client):
    """When all syllabus items are checked, next should generate eval article."""
    all_checked = "# 测试 · 课程大纲\n\n## 核心掌握项\n\n### 模块一\n- [x] 能够解释概念"
    course_id = _setup_course(auth_client, syllabus_content=all_checked)

    # Update syllabus to all-checked
    auth_client.put(f"/api/courses/{course_id}/syllabus", json={"content": all_checked})

    eval_stream = _make_mock_stream(["<!-- eval-article -->\n\n# 最终评估\n\n评估内容"])

    with patch("app.courses.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = eval_stream
        mock_get_client.return_value = mock_client

        res = auth_client.post(f"/api/courses/{course_id}/next")
        assert res.status_code == 200
        body = res.text
        assert '"done": true' in body
        assert '"is_evaluation": true' in body

    # Verify eval lesson created
    lessons = auth_client.get(f"/api/courses/{course_id}/lessons").json()
    assert len(lessons) == 2
    assert lessons[1]["is_evaluation"] is True


def test_get_summary_not_found(auth_client):
    """Summary should 404 when course not completed."""
    course_id = _setup_course(auth_client)
    res = auth_client.get(f"/api/courses/{course_id}/summary")
    assert res.status_code == 404


def test_summary_generation_after_eval(auth_client):
    """After eval article, next should generate summary and mark course completed."""
    course_id = _setup_course(auth_client)

    # Manually add an eval lesson
    from app.models import Lesson
    import app.database as app_database
    with app_database.SessionLocal() as db:
        eval_lesson = Lesson(
            course_id=course_id, number=2,
            content="<!-- eval-article -->\n# 评估", is_evaluation=True,
        )
        db.add(eval_lesson)
        db.commit()

    summary_stream = _make_mock_stream(["# 学习总结\n\n知识图谱..."])

    with patch("app.courses.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = summary_stream
        mock_get_client.return_value = mock_client

        res = auth_client.post(f"/api/courses/{course_id}/next")
        assert res.status_code == 200
        body = res.text
        assert '"done": true' in body
        assert '"completed": true' in body

    # Verify summary exists and course is completed
    res = auth_client.get(f"/api/courses/{course_id}/summary")
    assert res.status_code == 200
    assert "总结" in res.json()["content"]

    detail = auth_client.get(f"/api/courses/{course_id}").json()
    assert detail["status"] == "completed"
