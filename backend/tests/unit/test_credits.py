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


def test_deduct_credits_success():
    """Direct unit test: deduct_credits returns True when balance is sufficient."""
    from tests.conftest import TestSession, engine
    from app.database import Base
    from app.models import User
    from app.credits import deduct_credits

    Base.metadata.create_all(bind=engine)
    try:
        db = TestSession()
        user = User(email="deduct@example.com", username="deductuser", password_hash="x", credits=50)
        db.add(user)
        db.commit()
        db.refresh(user)

        result = deduct_credits(db, user.id, 10, "test deduction")
        db.commit()
        assert result is True

        # Verify new balance
        db.refresh(user)
        assert user.credits == 40
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_deduct_credits_insufficient_balance():
    """Direct unit test: deduct_credits returns False when balance is insufficient."""
    from tests.conftest import TestSession, engine
    from app.database import Base
    from app.models import User
    from app.credits import deduct_credits

    Base.metadata.create_all(bind=engine)
    try:
        db = TestSession()
        user = User(email="broke@example.com", username="brokeuser", password_hash="x", credits=5)
        db.add(user)
        db.commit()
        db.refresh(user)

        result = deduct_credits(db, user.id, 10, "should fail")
        db.commit()
        assert result is False

        # Balance unchanged
        db.refresh(user)
        assert user.credits == 5
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_deduct_credits_exact_balance():
    """Direct unit test: deduct_credits succeeds when amount equals balance exactly."""
    from tests.conftest import TestSession, engine
    from app.database import Base
    from app.models import User
    from app.credits import deduct_credits

    Base.metadata.create_all(bind=engine)
    try:
        db = TestSession()
        user = User(email="exact@example.com", username="exactuser", password_hash="x", credits=10)
        db.add(user)
        db.commit()
        db.refresh(user)

        result = deduct_credits(db, user.id, 10, "exact deduction")
        db.commit()
        assert result is True

        db.refresh(user)
        assert user.credits == 0

        # Now another deduction should fail
        result2 = deduct_credits(db, user.id, 1, "should fail")
        db.commit()
        assert result2 is False
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
