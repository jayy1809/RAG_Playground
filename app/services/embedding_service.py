from typing import List, Optional, Dict, Any
from app.config.settings import settings
import httpx
from fastapi import HTTPException
import asyncio
import logging
from pinecone import Pinecone
import time
import json
from datetime import datetime
from pinecone_text.sparse import BM25Encoder

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.pinecone_api_key = settings.PINECONE_API_KEY
        self.dense_embed_url = settings.PINECONE_EMBED_URL
        self.pinecone_embedding_url = settings.PINECONE_EMBED_URL
        self.pinecone_api_version = settings.PINECONE_API_VERSION


    async def pinecone_dense_embeddings(self, 
                                        inputs: list, 
                                        embedding_model: str = "llama-text-embed-v2" , 
                                        input_type:str = "passage", 
                                        truncate:str = "END", 
                                        dimension: int = 2048):
        payload = {
            "model": embedding_model,
            "parameters": {
                "input_type": input_type,
                "truncate": truncate,
                "dimension": dimension
            },
            "inputs": inputs
        }
        
        headers = {
            "Api-Key": self.pinecone_api_key,
            "Content-Type": "application/json",
            "X-Pinecone-API-Version": self.pinecone_api_version
        }
        
        url = self.dense_embed_url

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                print("embeddings generated")
                return response.json()
            
        except httpx.HTTPStatusError as e:
                parsed_response = json.loads(response.content.decode("utf-8"))
                error_message = parsed_response.get("error", {}).get("message", "Unknown error occurred")
                logging.error(f"Error creating index: {error_message}")
                raise HTTPException(status_code=400, detail = error_message)
        except Exception as e:
            logging.error(f"Error creating index: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        


    def pinecone_sparse_embeddings(self, inputs):

        try:
            text_list = []
            for input in inputs:
                    text = input.get("text")
                    text_list.append(text)

            bm25 = BM25Encoder.default()
            sparse_vector = bm25.encode_documents(text_list)
            return sparse_vector
        
        except Exception as e:
            logging.error(f"Error creating index: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        