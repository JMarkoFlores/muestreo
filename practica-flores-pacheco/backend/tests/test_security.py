from app.security import hash_password, verify_password

def test_password_hash_roundtrip():
    stored = hash_password("postgres")
    assert stored != "postgres"
    assert verify_password("postgres", stored)
    assert not verify_password("incorrecta", stored)
