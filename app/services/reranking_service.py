import json
import logging
from urllib.parse import urljoin

import httpx
from fastapi import HTTPException

from app.config.settings import settings

logger = logging.getLogger(__name__)


class RerankerService:
    def __init__(self):
        self.pinecone_api_key = settings.PINECONE_API_KEY
        self.cohere_api_key = settings.COHERE_API_KEY
        self.jina_api_key = settings.JINA_API_KEY
        self.pinecone_rerank_url = settings.PINECONE_RERANK_URL
        self.pinecone_api_version = settings.PINECONE_API_VERSION
        self.cohere_base_url = settings.COHERE_BASE_URL
        self.jina_base_url = settings.JINA_BASE_URL
        self.RERANK_SUFFIX = "rerank"

    async def pinecone_reranker(
        self, model_name: str, query: str, documents: list, top_n: int
    ):

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Pinecone-API-Version": self.pinecone_api_version,
            "Api-Key": self.pinecone_api_key,
        }

        payload = {
            "model": model_name,
            "query": query,
            "return_documents": True,
            "top_n": top_n,
            "documents": documents,
            "parameters": {
                "truncate": "END",
            },
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
            error_message = parsed_response.get("error", {}).get(
                "message", "Unknown error occurred"
            )
            logging.error(f"Error creating index: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        except Exception as e:
            logging.error(f"Error creating index: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def cohere_rerank(
        self, model_name: str, query: str, documents: list, top_n: int
    ):
        # query will be string and documents will be list of strings
        rerank_url = urljoin(self.cohere_base_url, self.RERANK_SUFFIX)

        headers = {
            "content-type": "application/json",
            "accept": "application/json",
            "X-Pinecone-API-Version": "2025-01",
            "Authorization": f"bearer {self.cohere_api_key}",
        }

        payload = {
            "model": model_name,
            "query": query,
            "top_n": top_n,
            "documents": documents,
        }

        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    rerank_url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                print("reranking done by cohere")
                return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error: {e.response.status_code} - {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code, detail=str(e)
            )
        except httpx.RequestError as e:
            logging.error(f"Request error:  {str(e)}")
            raise HTTPException(
                status_code=502, detail="Failed to connect to API"
            )
        except Exception as e:
            logging.error(f"Error in reranking in cohere {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def jina_rerank(
        self, model_name: str, query: str, documents: list, top_n: int
    ):
        # query will be string and documents will be list of strings
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jina_api_key}",  # f"Bearer {os.getenv('JINA_API_KEY')}",
        }

        payload = {
            "model": model_name,
            "query": query,
            "top_n": top_n,
            "documents": documents,
        }

        rerank_url = urljoin(self.jina_base_url, self.RERANK_SUFFIX)

        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    rerank_url, headers=headers, json=payload
                )
                response.raise_for_status()
                print("reranking done by jina")
                return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error: {e.response.status_code} - {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code, detail=str(e)
            )
        except httpx.RequestError as e:
            logging.error(f"Request error:  {str(e)}")
            raise HTTPException(
                status_code=502, detail="Failed to connect to API"
            )
        except Exception as e:
            logging.error(f"Error in reranking in jina {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
