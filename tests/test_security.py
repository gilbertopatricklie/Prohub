import jwt

from app.security import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM

def test_password_hasing():
    password = "password-secret"
    
    hashed_password = hash_password(password)
    
    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("password-salah", hashed_password)
    
def test_access_token_contain_userid():
    user_id = 123
    token = create_access_token(user_id)
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    assert payload["sub"] == str(user_id)
    assert "exp" in payload