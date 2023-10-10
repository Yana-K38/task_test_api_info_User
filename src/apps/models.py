import re
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.exc import DatabaseError, IntegrityError, InternalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from sqlalchemy.sql import text

from src.apps.schemas import UserSchema
from src.db import Base

Base = declarative_base()


class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    hashed_password: str = Column(String(length=1024), nullable=False)
    avatar = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)

    @validates("phone_number")
    def validate_phone_number(self, key, phone_number):
        if re.match(r"^\+7\d{10}$", phone_number):
            return phone_number
        else:
            raise ValueError(
                "Номер телефона должен начинаться с '+7' и состоять из 11 цифр (включая код страны)"
            )
