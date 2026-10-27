from datetime import datetime
from sqlalchemy import DateTime, Integer, Numeric, String, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Product(Base):
    __tablename__="products"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
class User(Base):
    __tablename__="users"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )