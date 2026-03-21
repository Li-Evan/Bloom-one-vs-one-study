def test_get_balance(auth_client):
    res = auth_client.get("/api/credits/balance")
    assert res.status_code == 200
    assert res.json()["credits"] == 100


def test_get_history(auth_client):
    res = auth_client.get("/api/credits/history")
    assert res.status_code == 200
    history = res.json()
    assert len(history) == 1
    assert history[0]["type"] == "registration_bonus"
    assert history[0]["amount"] == 100


def test_balance_no_auth(client):
    res = client.get("/api/credits/balance")
    assert res.status_code in (401, 403)
