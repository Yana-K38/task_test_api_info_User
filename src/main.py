from fastapi import FastAPI
import uvicorn


app = FastAPI(
    title="API сервис на Python, который будет предоставлять CRUD операции для работы с базой данных, содержащей информацию о пользователях.",
    docs_url="/docs",
    redoc_url="/redoc",
)



if __name__ == "__main__":
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
    )