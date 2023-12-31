from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.apps import schemas
from src.apps.models import UserTable
from src.db import get_async_session
from src.logger import logger
from src.services.auth import current_user
from src.services.sorted import sorted_query

router_user = APIRouter(
    tags=["Users"],
    prefix="/users",
)


@router_user.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.UserSchema],
)
async def get_all_users(
    session: AsyncSession = Depends(get_async_session),
    filter_username: str = Query(None, description="Фильтр по имени пользователя"),
    filter_active: bool = Query(None, description="Фильтр по активности"),
    sort_by: str = Query(None, description="Поле для сортировки"),
):
    """
    Получение списка всех пользователей.

    Args:
        session (AsyncSession, optional): Асинхронная сессия SQLAlchemy.
        filter_username (str, optional): Фильтр по имени пользователя.
        filter_active (bool, optional): Фильтр по активности.
        sort_by (str, optional): Поле для сортировки.

    Returns:
        List[schemas.UserSchema]: Список моделей данных всех пользователей в системе.
    """
    sql_query = text(
        """
        SELECT id, username, email, avatar, phone_number, is_active, is_superuser, is_verified
        FROM users
        """
    )
    sql_query = sorted_query(sort_by)
    parameters = {}

    if filter_username:
        sql_query += " WHERE LOWER(username) = LOWER(:filter_username)"
        parameters["filter_username"] = filter_username

    if filter_active is not None:
        if "WHERE" in sql_query:
            sql_query += " AND is_active = :filter_active"
        else:
            sql_query += " WHERE is_active = :filter_active"
        parameters["filter_active"] = filter_active
    try:
        result = await session.execute(text(sql_query), parameters)
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
    except Exception as e:
        logger.error(f"Error in get_all_users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router_user.get(
    "/{id}/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserSchema,
)
async def get_user_by_id(id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Получение информации о пользователе по его ID.

    Args:
        id (int): Идентификатор пользователя.
        session (AsyncSession, optional): Асинхронная сессия SQLAlchemy.

    Returns:
        schemas.UserSchema: Модель данных пользователя.

    Raises:
        HTTPException: Если пользователь с указанным ID не найден.
    """
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
        logger.info("User not found", extra={"status_code": 404})
        raise HTTPException(status_code=404, detail="User not found")
    user_dict = dict(user_row)
    user_schema = schemas.UserSchema(**user_dict)
    return user_schema


@router_user.get("/me", response_model=schemas.UserSchema)
async def get_current_user(
    user: UserTable = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Получение информации о текущем пользователе.

    Args:
        user (UserTable): Текущий авторизованный пользователь.
        session (AsyncSession, optional): Асинхронная сессия SQLAlchemy.

    Returns:
        schemas.UserSchema: Модель данных текущего пользователя.

    Raises:
        HTTPException: Если текущий пользователь не найден.
    """
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
        logger.info("User not found", extra={"status_code": 404})
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
    """
    Обновление информации о текущем пользователе.

    Args:
        user_update (schemas.UserUpdate): Модель данных с обновленной информацией о пользователе.
        user (UserTable): Текущий авторизованный пользователь.
        session (AsyncSession, optional): Асинхронная сессия SQLAlchemy.

    Returns:
        schemas.UserSchema: Модель данных обновленного пользователя.

    Raises:
        HTTPException: Если обновление пользователя не удалось.
    """
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
    """
    Удаление текущего пользователя.

    Args:
        user (UserTable): Текущий авторизованный пользователь.
        session (AsyncSession, optional): Асинхронная сессия SQLAlchemy.

    Returns:
        dict: Словарь с сообщением об успешном удалении текущего пользователя.

    Raises:
        HTTPException: Если удаление текущего пользователя не удалось.
    """
    query = text(
        """
        DELETE FROM users WHERE id = :user_id
        """
    ).bindparams(user_id=user.id)

    await session.execute(query)
    await session.commit()
    return {"message": "User deleted"}


@router_user.delete("/{id}")
async def delete_user_by_id(
    id: int,
    user: UserTable = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаление пользователя по ID.

    Args:
        id (int): Идентификатор пользователя, которого необходимо удалить.
        user (UserTable, optional): Текущий пользователь, авторизованный в системе.
        session (AsyncSession, optional): Асинхронная сессия SQLAlchemy.

    Raises:
        HTTPException: Если текущий пользователь не является суперпользователем и не соответствует ID пользователя для удаления.

    Returns:
        dict: Словарь с сообщением об успешном удалении пользователя.
    """
    if not (user.is_superuser or id == user.id):
        logger.info("You don't have the rights to do this", extra={"status_code": 403})
        raise HTTPException(
            status_code=403, detail="You don't have the rights to do this."
        )
    query = text(
        """
        DELETE FROM users WHERE id = :user_id
        """
    ).bindparams(user_id=id)
    await session.execute(query)
    await session.commit()
    return {"message": "User deleted"}


@router_user.get(
    "/search_user",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.UserSchema],
)
async def search_users(
    search_query: str = Query(..., min_length=1, description="Search query"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Поиск пользователей по имени пользователя.

    Args:
        search_query (str): Строка для поиска пользователей.

    Returns:
        List[schemas.UserSchema]: Список найденных пользователей.
    """
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
        logger.info(
            "There is no user with this name in the database.",
            extra={"status_code": 404},
        )
        raise HTTPException(
            status_code=404, detail="There is no user with this name in the database."
        )
    return user_list
