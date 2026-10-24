from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import initialize_database
from students import router as students_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(students_router)


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "My first rest API"}