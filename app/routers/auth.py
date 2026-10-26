from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreation, UserResponse, LoginRequest
from app.security import hash_password, create_access_token, verify_password
from app.dependencies import get_current_user

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

@router.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    statement = select(User).where(User.email == payload.email)
    user = db.scalars(statement).first()
    
    if user is None or not verify_password(payload.password,user.hashed_password):
        raise HTTPException(status_code=401,
                            detail="Unauthorized (Incorrect email or password)",
                            headers={"WWW-Authenticate": "Bearer"})
        
    access_token = create_access_token(user.id)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user