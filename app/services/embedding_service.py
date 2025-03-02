import json
import logging
from urllib.parse import urljoin

import httpx
from fastapi import HTTPException
from pinecone_text.sparse import BM25Encoder

from app.config.settings import settings

logger = logging.getLogger(__name__)

bm25 = BM25Encoder.default()


class EmbeddingService:
    def __init__(self):
        self.pinecone_api_key = settings.PINECONE_API_KEY
        self.dense_embed_url = settings.PINECONE_EMBED_URL
        self.pinecone_embedding_url = settings.PINECONE_EMBED_URL
        self.pinecone_api_version = settings.PINECONE_API_VERSION
        self.cohere_base_url = settings.COHERE_BASE_URL
        self.cohere_api_key = settings.COHERE_API_KEY
        self.jina_api_key = settings.JINA_API_KEY
        self.jina_base_url = settings.JINA_BASE_URL
        self.EMBED_SUFFIX = "embed"
        self.JINA_EMBED_SUFFIX = "embeddings"

    async def pinecone_dense_embeddings(
        self,
        inputs: list,
        embedding_model: str = "llama-text-embed-v2",
        input_type: str = "passage",
        truncate: str = "END",
        dimension: int = 1024,
    ):
        payload = {
            "model": embedding_model,
            "parameters": {
                "input_type": input_type,
                "truncate": truncate,
                "dimension": dimension,
            },
            "inputs": inputs,
        }

        headers = {
            "Api-Key": self.pinecone_api_key,
            "Content-Type": "application/json",
            "X-Pinecone-API-Version": self.pinecone_api_version,
        }

        url = self.dense_embed_url

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                print("embeddings generated")
                response = response.json()
                list_result = [item["values"] for item in response["data"]]
                return list_result

        except httpx.HTTPStatusError as e:
            parsed_response = json.loads(response.content.decode("utf-8"))
            error_message = parsed_response.get("error", {}).get(
                "message", "Unknown error occurred"
            )
            logging.error(f"Error dense embeddings: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        except Exception as e:
            logging.error(f"Error dense embeddings: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def pinecone_sparse_embeddings(self, inputs):
        try:
            sparse_vector = bm25.encode_documents(inputs)
            return sparse_vector

        except Exception as e:
            logging.error(f"Error creating sparse embeddings: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def cohere_dense_embeddings(
        self,
        model_name: str,
        texts: list[str],
        input_type: str = "search_document",
    ):

        url = urljoin(self.cohere_base_url, self.EMBED_SUFFIX)

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.cohere_api_key}",
        }
        data = {
            "model": model_name,
            "texts": texts,
            "input_type": input_type,
            "embedding_types": ["float"],
        }

        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                # return response.json()
                response = response.json()
                result = response["embeddings"]["float"]
                return result
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
            logging.error(f"Error creating dense cohere embeddings {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def jina_dense_embeddings(
        self, model_name: str, dimension: int, inputs: list[str]
    ):

        url = urljoin(self.cohere_base_url, self.JINA_EMBED_SUFFIX)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jina_api_key}",
        }
        data = {
            "model": model_name,
            "dimensions": dimension,
            "normalized": True,
            "embedding_type": "float",
            "input": inputs,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                # return response.json()
                response = response.json()
                result = [item["embedding"] for item in response["data"]]
                return result

        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error: {e.response.status_code} - {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code, detail=str(e)
            )
        except httpx.RequestError as e:
            logging.error(f"Request error:  {str(e)}")
            raise HTTPException(
                status_code=502,  # Bad Gateway (Failed to connect)
                detail="Failed to connect to API",
            )
        except Exception as e:
            logging.error(f"Error creating dense jina embeddings {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
