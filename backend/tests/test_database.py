from sqlalchemy import text


def test_engine_connects(test_engine):
    with test_engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_session_works(test_session):
    result = test_session.execute(text("SELECT 1"))
    assert result.scalar() == 1
