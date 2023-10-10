from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.apps import schemas
from src.apps.models import UserTable
from src.db import get_async_session
from src.services.auth import current_user

router_user = APIRouter(
    tags=["Users"],
    prefix="/users",
)


@router_user.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.UserSchema],
)
async def get_all_users(session: AsyncSession = Depends(get_async_session)):
    query = text(
        """
            SELECT id, username, email, avatar, phone_number, is_active, is_superuser, is_verified
            FROM users
            """
    )
    result = await session.execute(query)
    user_dicts = result.mappings().fetchall()
    users = [
        schemas.UserSchema(
            id=user_dict["id"],
            username=user_dict["username"],
            email=user_dict["email"],
            avatar=user_dict["avatar"],
            phone_number=user_dict["phone_number"],
            is_active=user_dict["is_active"],
            is_superuser=user_dict["is_superuser"],
            is_verified=user_dict["is_verified"],
        )
        for user_dict in user_dicts
    ]
    return users


@router_user.get(
    "/{id}/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserSchema,
)
async def get_user_by_id(id: int, session: AsyncSession = Depends(get_async_session)):
    query = text(
        """
            SELECT id, username, email, avatar, phone_number, is_active, is_superuser, is_verified
            FROM users
            WHERE id=:id
            """
    ).bindparams(id=id)
    row: CursorResult = await session.execute(query)
    user_row = row.mappings().fetchone()
    if user_row is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_dict = dict(user_row)
    user_schema = schemas.UserSchema(**user_dict)
    return user_schema


@router_user.get("/me", response_model=schemas.UserSchema)
async def get_current_user(
    user: UserTable = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = text(
        """
        SELECT id, email, username, avatar, phone_number, is_active, is_superuser, is_verified
        FROM users
        WHERE id=:user_id
        """
    ).bindparams(user_id=user.id)
    row: CursorResult = await session.execute(query)
    user_row = row.mappings().fetchone()
    if user_row is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_dict = dict(user_row)
    user_schema = schemas.UserSchema(**user_dict)
    return user_schema


@router_user.put("/me", response_model=schemas.UserSchema)
async def update_current_user(
    user_update: schemas.UserUpdate,
    user: UserTable = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = text(
        """
        UPDATE users
        SET
            email = :email,
            username = :username,
            avatar = :avatar,
            phone_number = :phone_number,
            is_active = :is_active,
            is_verified = :is_verified
        WHERE id = :user_id
        """
    ).bindparams(
        email=user_update.email,
        username=user_update.username,
        avatar=user_update.avatar,
        phone_number=user_update.phone_number,
        is_active=user_update.is_active,
        is_verified=user_update.is_verified,
        user_id=user.id,
    )
    await session.execute(query)
    await session.commit()
    updated_user = await get_current_user(user=user, session=session)
    return updated_user


@router_user.delete("/me")
async def delete_current_user(
    user: UserTable = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = text(
        """
        DELETE FROM users WHERE id = :user_id
        """
    ).bindparams(user_id=user.id)

    await session.execute(query)
    await session.commit()
    return {"message": "Пользователь удален"}


@router_user.delete("/{id}")
async def delete_user_by_id(
    id: int,
    user: UserTable = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not (user.is_superuser or id == user.id):
        raise HTTPException(status_code=403, detail="У вас нет прав на это действие.")
    query = text(
        """
        DELETE FROM users WHERE id = :user_id
        """
    ).bindparams(user_id=id)
    await session.execute(query)
    await session.commit()
    return {"message": "Пользователь удален"}


@router_user.get(
    "/search_user",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.UserSchema],
)
async def search_users(
    search_query: str = Query(..., min_length=1, description="Search query"),
    session: AsyncSession = Depends(get_async_session),
):
    query = text(
        """
        SELECT * 
        FROM users
        WHERE username LIKE '%' || :search_query || '%'
        """
    )
    rows: CursorResult = await session.execute(
        query, {"search_query": f"%{search_query}%"}
    )
    user_list = []
    for user_row in rows.fetchall():
        user_dict = {
            "id": user_row.id,
            "email": user_row.email,
            "username": user_row.username,
            "avatar": user_row.avatar,
            "phone_number": user_row.phone_number,
            "is_active": user_row.is_active,
            "is_superuser": user_row.is_superuser,
            "is_verified": user_row.is_verified,
        }
        user_schema = schemas.UserSchema(**user_dict)
        user_list.append(user_schema)
    if not user_list:
        return {"message": "Пользователя с таким username не найдено."}
    return user_list
