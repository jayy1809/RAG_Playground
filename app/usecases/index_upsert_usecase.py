from app.config.database import db_helper
from app.models.domain.indexupsert import IndexUpsert, Namespace, NamespaceDetails
from fastapi import HTTPException, Depends, status
from fastapi.responses import JSONResponse
from app.repositories.index_upsert_repository import IndexUpsertRepository
from app.services.pinecone_service import PineconeService
from app.services.embedding_service import EmbeddingService
import asyncio

class IndexUpsertUseCase:
    def __init__(
            self, 
            index_upsert_repository = Depends(IndexUpsertRepository),
            pinecone_service = Depends(PineconeService),
            embedding_service = Depends(EmbeddingService)
        ):
        self.index_upsert_repository = index_upsert_repository
        self.pinecone_service = pinecone_service
        self.embedding_service = embedding_service
        self.file_path = "uploads/raw_dataset.json"
        self.chunk_size = 90
        self.semaphore = asyncio.Semaphore(5)
        self.model_provider = {
            "llama-text-embed-v2": "pinecone",
            "multilingual-e5-large": "pinecone",
            "embed-english-v3.0": "cohere",
            "embed-english-light-v3.0": "cohere",
            "embed-english-v2.0": "cohere",
            "embed-english-light-v2.0": "cohere",
            "embed-multilingual-v3.0": "cohere",
            "embed-multilingual-light-v3.0": "cohere",
            "embed-multilingual-v2.0": "cohere",
            "jina-embeddings-v3": "jina",
            "jina-embeddings-v2-base-code": "jina",
        }
            
    async def process_chunk(self, chunk, provider, embed_model, dimension=None):
        async with self.semaphore:
            if provider == "pinecone":
                return await self.embedding_service.pinecone_dense_embeddings(chunk, embed_model, dimension=dimension)
            elif provider == "cohere":
                return await self.embedding_service.cohere_dense_embeddings(embed_model, chunk)
            elif provider == "jina":
                return await self.embedding_service.jina_embeddings(embed_model, dimension, chunk)

    async def _get_embeddings(self, data, embed_model, dimension):
        all_embeddings = []
        embedding_provider = self.model_provider.get(embed_model)
        
        if embedding_provider == "pinecone":
            inputs = [{"text": item["text_content"]} for item in data]
        elif embedding_provider == "cohere":
            inputs = [item["text"] for item in data]
        elif embedding_provider == "jina":
            inputs = [{"text": item["text_content"]} for item in data]
        else:
            return []
        
        chunks = [inputs[i:i + self.chunk_size] for i in range(0, len(inputs), self.chunk_size)]
        tasks = [self.process_chunk(chunk, embedding_provider, embed_model, dimension) for chunk in chunks]
        chunk_results = await asyncio.gather(*tasks)
        
        for embeddings in chunk_results:
            all_embeddings.extend(embeddings)
            
        return all_embeddings

    async def _prepare_and_upsert(self, data, embed_model, dimension, index_host, namespace_name):
        all_embeddings = await self._get_embeddings(data, embed_model, dimension)
        
        text_list = [item["text"] for item in data]
        sparse_embeds = self.embedding_service.pinecone_sparse_embeddings(text_list)

        final_upsert_format = await self.pinecone_service.upsert_format(data, all_embeddings, sparse_embeds)
        return await self.pinecone_service.upsert_vectors(index_host, final_upsert_format, namespace_name)

    async def _create_namespace_and_save(self, file_name, embed_model, index_name, index_host, dimension, similarity_metric):
        namespace_name = f"{file_name}-{embed_model}-namespace"
        
        namespace = Namespace(
            name=namespace_name,
            filename=file_name,
            embedding_model=embed_model
        )
        
        index_upsert = IndexUpsert(
            index_name=index_name,
            index_host=index_host,
            dimension=dimension,
            similarity_metric=similarity_metric
        )
        
        index_upsert.add_namespace(namespace)
        return await self.index_upsert_repository.add_index_upsert_details(index_upsert), namespace_name

    async def index_upsert(self, request):
        dimension = request.dimension
        similarity_metric = request.similarity_metric
        file_name = request.file_name
        embed_model = request.embed_model

        already_upserted = await self.index_upsert_repository.find_matching_index_upsert(
            dimension, similarity_metric, file_name, embed_model
        )

        if already_upserted:
            return {"message": "such dimension, similarity metric, filename and embed_model configuration already exists, move on to query"}
        
        with open(self.file_path, "r") as file:
            data = file.read()

        already_index = await self.index_upsert_repository.find_matching_index(dimension, similarity_metric)
        
        if not already_index:
            index_name = f"{similarity_metric}-{dimension}"
            response = await self.pinecone_service.create_index(index_name, dimension, similarity_metric)
            index_host = response.get("host")
            
            db_result, namespace_name = await self._create_namespace_and_save(
                file_name, embed_model, index_name, index_host, dimension, similarity_metric
            )
            
            upsert_result = await self._prepare_and_upsert(
                data, embed_model, dimension, index_host, namespace_name
            )
            
            return {"upsert_result": upsert_result, "database_result": db_result}
        
        index_name = already_index.get("index_name")
        index_host = already_index.get("index_host")
        
        db_result, namespace_name = await self._create_namespace_and_save(
            file_name, embed_model, index_name, index_host, dimension, similarity_metric
        )
        
        upsert_result = await self._prepare_and_upsert(
            data, embed_model, dimension, index_host, namespace_name
        )
        
        return {"upsert_result": upsert_result, "database_result": db_result}