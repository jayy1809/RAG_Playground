from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PINECONE_API_KEY : str
    GROQ_API_KEY : str
    LLAMA_CLOUD_API_KEY : str
    COHERE_API_KEY : str
    ZILLIS_API_KEY : str
    JINA_AI_API_KEY : str
    UNSTRUCTURED_API_KEY : str
    GEMINI_API_KEY : str
    MONGO_URI :str
    DB_NAME :str
    PINECONE_CREATE_INDEX_URL : str
    PINECONE_API_VERSION : str
    PINECONE_EMBED_URL : str
    PINECONE_UPSERT_URL : str
    PINECONE_RERANK_URL : str
    PINECONE_QUERY_URL : str
    PINECONE_LIST_INDEXES_URL : str

    class Config:
        env_file = ".env"

settings = Settings()