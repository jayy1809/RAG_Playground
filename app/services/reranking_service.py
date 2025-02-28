import httpx
from app.config.settings import settings
import logging
from fastapi import HTTPException
import json

logger = logging.getLogger(__name__)


class RerankerService():
    def __init__(self):
        self.pinecone_api_key = settings.PINECONE_API_KEY
        self.pinecone_rerank_url = settings.PINECONE_RERANK_URL
        self.pinecone_api_version = settings.PINECONE_API_VERSION


    async def pinecone_reranker(self, model_name: str, query: str, documents: list, top_n: int):
    
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Pinecone-API-Version": self.pinecone_api_version,
            "Api-Key": self.pinecone_api_key
        }

        payload = {
            "model": model_name,
            "query": query,
            "return_documents": True,
            "top_n": top_n,
            "documents": documents,
            "parameters": {
                "truncate": "END",
            }
        }

        url = self.pinecone_rerank_url

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                print("reranking done")
                return response.json()
        
        except httpx.HTTPStatusError as e:
                parsed_response = json.loads(response.content.decode("utf-8"))
                error_message = parsed_response.get("error", {}).get("message", "Unknown error occurred")
                logging.error(f"Error creating index: {error_message}")
                raise HTTPException(status_code=400, detail = error_message)
        except Exception as e:
            logging.error(f"Error creating index: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))