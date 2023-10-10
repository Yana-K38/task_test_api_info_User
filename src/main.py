import uvicorn
from fastapi import FastAPI

from src.api.router import router_user
from src.apps.schemas import UserCreate, UserRead
from src.db import UserTable
from src.services.auth import auth_backend, current_user, fastapi_users

app = FastAPI(
    title="API сервис на Python, который будет предоставлять CRUD операции для работы с базой данных, содержащей информацию о пользователях.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(router_user)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
    )
