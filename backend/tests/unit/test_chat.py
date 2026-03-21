from unittest.mock import patch, MagicMock


def _make_mock_stream(content_chunks):
    """Create a mock OpenAI streaming response."""
    chunks = []
    for text in content_chunks:
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = text
        chunks.append(chunk)
    # Final chunk with no content to signal end
    final = MagicMock()
    final.choices = [MagicMock()]
    final.choices[0].delta.content = None
    chunks.append(final)
    return iter(chunks)


def test_chat_send_success(auth_client):
    # Create a course first
    course = auth_client.post("/api/courses", json={"name": "测试课程"}).json()
    course_id = course["id"]

    mock_stream = _make_mock_stream(["你好", "，同学"])

    with patch("app.chat.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_stream
        mock_get_client.return_value = mock_client

        res = auth_client.post("/api/chat/send", json={
            "course_id": course_id,
            "message": "我想学习博弈论",
        })
        assert res.status_code == 200
        assert "text/event-stream" in res.headers["content-type"]

        # Verify stream content
        body = res.text
        assert "你好" in body
        assert "同学" in body
        assert '"done": true' in body

        # Verify LLM client was called with correct params
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["stream"] is True
        assert any(m["role"] == "system" for m in call_kwargs.kwargs["messages"])

    # Verify credit was deducted
    balance = auth_client.get("/api/credits/balance").json()
    assert balance["credits"] == 99  # Started with 100, deducted 1

    # Verify user message was saved
    messages = auth_client.get(f"/api/courses/{course_id}/messages").json()
    assert len(messages) >= 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "我想学习博弈论"


def test_chat_send_insufficient_credits(auth_client):
    """User with 0 credits should get 402."""
    course = auth_client.post("/api/courses", json={"name": "测试课程"}).json()
    course_id = course["id"]

    # Drain all credits by sending 100 messages (mock the LLM)
    mock_stream = _make_mock_stream(["ok"])
    with patch("app.chat.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_stream
        mock_get_client.return_value = mock_client

        for i in range(100):
            mock_client.chat.completions.create.return_value = _make_mock_stream(["ok"])
            auth_client.post("/api/chat/send", json={
                "course_id": course_id,
                "message": f"msg {i}",
            })

    # Now credits should be 0
    balance = auth_client.get("/api/credits/balance").json()
    assert balance["credits"] == 0

    # Next request should fail with 402
    res = auth_client.post("/api/chat/send", json={
        "course_id": course_id,
        "message": "this should fail",
    })
    assert res.status_code == 402
    assert "积分不足" in res.json()["detail"]


def test_chat_send_nonexistent_course(auth_client):
    res = auth_client.post("/api/chat/send", json={
        "course_id": 9999,
        "message": "hello",
    })
    assert res.status_code == 404


def test_chat_send_no_auth(client):
    res = client.post("/api/chat/send", json={
        "course_id": 1,
        "message": "hello",
    })
    assert res.status_code in (401, 403)
