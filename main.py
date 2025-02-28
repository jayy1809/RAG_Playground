from fastapi import FastAPI
from app.apis.file_upload import router as file_router

app = FastAPI()

app.include_router(file_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG Playground"}