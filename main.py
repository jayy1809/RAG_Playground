from fastapi import FastAPI
from app.apis.file_upload import router as file_router
from contextlib import asynccontextmanager
from app.config.database import db_helper

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_helper.connect()
    db = await db_helper.get_db()
    yield
    await db_helper.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(file_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG Playground"}