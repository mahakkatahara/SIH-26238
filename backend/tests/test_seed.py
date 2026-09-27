from app.seed import seed_database
from app.models.user import User
from app.models.scholarship import Scholarship


def test_seed_database_idempotent(db_session):
    # First seed
    res1 = seed_database(db_session, reset=False)
    assert res1["users"] >= 1
    assert res1["scholarships"] >= 1

    # Second seed without reset should insert 0 new records
    res2 = seed_database(db_session, reset=False)
    assert res2["users"] == 0
    assert res2["scholarships"] == 0
    assert res2["applications"] == 0

    # Reset seed
    res3 = seed_database(db_session, reset=True)
    assert res3["users"] == 1
    assert res3["scholarships"] == 4
