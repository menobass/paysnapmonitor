from app.db import db

def test_ban_user():
    db.ban_user("testuser")
    assert db.is_banned("testuser")
