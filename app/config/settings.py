from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PINECONE_API_KEY : str
    GROQ_API_KEY : str
    LLAMA_CLOUD_API_KEY : str
    COHERE_API_KEY : str
    ZILLIS_API_KEY : str
    JINA_API_KEY : str
    UNSTRUCTURED_API_KEY : str
    GEMINI_API_KEY : str
    # MONGO_URI :str
    # DB_NAME :str

    PINECONE_CREATE_INDEX_URL : str
    PINECONE_API_VERSION : str
    PINECONE_EMBED_URL : str
    PINECONE_UPSERT_URL : str
    PINECONE_RERANK_URL : str
    PINECONE_QUERY_URL : str
    PINECONE_LIST_INDEXES_URL : str
    COHERE_BASE_URL : str
    JINA_BASE_URL : str
    GROUND_TRUTH_CHUNK_SIZE: int = 10
    GROUND_TRUTH_CHUNK_SIZE: int = 4
    GROUND_TRUTH_FILE_STORE_PATH: str = "uploaded_data"
    GROUND_TRUTH_FILE_BASE_NAME: str ="gt_data"

    class Config:
        env_file = ".env"

settings = Settings()