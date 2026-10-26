from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreation, UserResponse
from app.security import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreation, db: Session = Depends(get_db)):
    statement = select(User).where(User.email == payload.email)
    existing_user = db.scalars(statement).first()
    
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="This email already registered")
    
    hashed_password = hash_password(payload.password)
    
    new_user = User(
        email = str(payload.email),
        hashed_password = hashed_password
    )
    
    db.add(new_user)
    
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This email already registered")
    
    return new_user