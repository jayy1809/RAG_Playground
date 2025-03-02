from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.apis import file_upload, index_upsert_route, query, reranking_router
from app.config.database import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_helper.connect()
    db = await db_helper.get_db()
    yield
    await db_helper.disconnect()


app = FastAPI(lifespan=lifespan)


app.include_router(query.router)
app.include_router(file_upload.router)
app.include_router(index_upsert_route.router)
app.include_router(reranking_router.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the RAG Playground"}
