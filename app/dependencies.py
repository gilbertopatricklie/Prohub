import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.security import SECRET_KEY, ALGORITHM

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
                     db: Session = Depends(get_db)) -> User:
    
    if credentials is None:
        raise HTTPException(status_code=401,
                            detail="Authentication required",
                            headers={"WWW-Authenticate": "Bearer"})
        
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        
        if not isinstance(subject, str) or not subject.isdecimal():
            raise InvalidTokenError("Invalid Subject")
        
        user_id = int(subject)
        
    except InvalidTokenError:
        raise HTTPException(status_code=401,
                            detail="Invalid or expired token",
                            headers={"WWW-Authenticate": "Bearer"})
        
    statement = select(User).where(User.id == user_id)
    user = db.scalars(statement).first()
    
    if user is None:
        raise HTTPException(status_code=401,
                            detail="User not found",
                            headers={"WWW-Authenticate": "Bearer"})
        
    if not user.is_active:
        raise HTTPException(status_code=403,
                            detail="User account is inactive")
    
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
        
    return current_user