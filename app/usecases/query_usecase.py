import traceback
from app.repositories.index_repository import IndexRepository
from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService
from app.services.evaluation_service import EvaluationService
from fastapi import Depends, HTTPException
from app.models.schemas.query_schema import QueryEndPointRequest


class QueryUseCase:
    
    def __init__(self, index_repository: IndexRepository = Depends(), embedding_service: EmbeddingService = Depends(), pinecone_service: PineconeService = Depends()):
        self.index_repository = index_repository
        self.embedding_service = embedding_service
        self.pinecone_service = pinecone_service
        self.embeddings_provider_mapping = {
            "llama-text-embed-v2" : "pinecone",
            "multilingual-e5-large" : "pinecone",
            "embed-english-v3.0" : "cohere",
            "embed-multilingual-v3.0" : "cohere",
            "embed-english-light-v3.0" : "cohere",
            "embed-multilingual-light-v3.0" : "cohere",
            "embed-english-v2.0" : "cohere",
            "embed-english-light-v2.0" : "cohere",
            "embed-multilingual-v2.0" : "cohere",
            "jina-embeddings-v3" : "jina",
        }

    
    async def execute(self, request_data: QueryEndPointRequest):
        """
        Main execution function for processing query endpoint requests.
        Breaks down the request handling into smaller, focused functions.
        """

        namespace_name, host = await self._get_namespace_and_host(request_data)

        dense_embedding = await self._generate_dense_embedding(request_data)
        
        results = None
        if request_data.is_hybrid:
            results = await self._perform_hybrid_search(
                request_data, namespace_name, host, dense_embedding
            )
        else:
            results = await self._perform_regular_search(
                request_data, namespace_name, host, dense_embedding
            )
        
        relevant_docs = []
        for result in results["matches"]:
            relevant_docs.append({
                "id": result["id"],
                "text": result["metadata"]["text"]
            })
        
        ground_truth = await self._get_ground_truth(request_data.query)
        
        if not relevant_docs:
            return {
                "relevant_docs": {},
                "error": "No relevant documents found."
            }
            
        if not ground_truth:
            return {
                "relevant_docs": relevant_docs,
                "error": "No ground truth data found. please enter a valid query to get the evaluation metrics."
            }
            
        evaluation_metrics = self._calculate_evaluation_metrics(
            relevant_docs, ground_truth, request_data.top_k
        )
            
        return {
            "relevant_docs": relevant_docs,
            **evaluation_metrics
        }

    async def _get_namespace_and_host(self, request_data: QueryEndPointRequest):
        """Get the namespace and host for the index."""
        
        index_name = f"{request_data.similarity_metric}-{request_data.dimension}"
        namespace_name, host = await self.index_repository.get_namespace_and_host(
            index_name, request_data.embedding_model, filename=request_data.filename
        )
        
        if not namespace_name:
            raise HTTPException(status_code=404, detail="Namespace not found.")
        
        return namespace_name, host

    async def _generate_dense_embedding(self, request_data: QueryEndPointRequest):
        """Generate dense embedding for the query using the appropriate provider."""
        
        embedding_provider = None
        for key, value in self.embeddings_provider_mapping.items():
            if key == request_data.embedding_model:
                embedding_provider = value
        
        if embedding_provider == "pinecone":
            return await self._generate_pinecone_embedding(request_data)
        elif embedding_provider == "cohere":
            return await self._generate_cohere_embedding(request_data)
        else:
            return await self._generate_jina_embedding(request_data)


    async def _generate_pinecone_embedding(self, request_data: QueryEndPointRequest):
        """Generate embeddings using Pinecone."""
        
        pinecone_input = [{"text": request_data.query}]
        embedding = await self.embedding_service.pinecone_dense_embeddings(
            inputs=pinecone_input,
            embedding_model=request_data.embedding_model,
            dimension=request_data.dimension,
            input_type="query"
        )
        return embedding[0]

    async def _generate_cohere_embedding(self, request_data: QueryEndPointRequest):
        """Generate embeddings using Cohere."""
        
        embedding = await self.embedding_service.cohere_dense_embeddings(
            texts=[request_data.query],
            model_name=request_data.embedding_model,
            input_type="search_query"
        )
        return embedding[0]

    async def _generate_jina_embedding(self, request_data: QueryEndPointRequest):
        """Generate embeddings using Jina."""
        
        embedding = await self.embedding_service.jina_dense_embeddings(
            model_name=request_data.embedding_model,
            dimension=request_data.dimension,
            inputs=[request_data.query],
            input_type="retrieval.query"
        )
        return embedding[0]


    async def _perform_hybrid_search(self, request_data, namespace_name, host, dense_embedding):
        """Perform hybrid search using both dense and sparse embeddings."""
        
        sparse_embedding = self.embedding_service.pinecone_sparse_embeddings(
            inputs=[request_data.query]
        )
        
        return await self.pinecone_service.pinecone_hybrid_query(
            index_host=host,
            namespace=namespace_name,
            top_k=request_data.top_k,
            alpha=request_data.alpha,
            query_vector_embeds=dense_embedding,
            query_sparse_embeds=sparse_embedding[0],
            include_metadata=request_data.include_metadata,
            filter_dict=request_data.filter_dict
        )

    async def _perform_regular_search(self, request_data, namespace_name, host, dense_embedding):
        """Perform regular dense vector search."""
        
        return await self.pinecone_service.pinecone_query(
            index_host=host,
            namespace=namespace_name,
            top_k=request_data.top_k,
            vector=dense_embedding,
            include_metadata=request_data.include_metadata,
            filter_dict=request_data.filter_dict
        )

    async def _get_ground_truth(self, query):
        """Fetch ground truth data for the query."""
        
        return await self.index_repository.fetch_ground_truth(query=query)

    def _calculate_evaluation_metrics(self, relevant_docs, ground_truth, top_k):
        """Calculate various evaluation metrics for the search results."""
        
        dummy_ground_truth = [
            {"id": 12, "chunk": "Quantum mechanics provides the foundation for quantum computing, leveraging superposition and entanglement to process information exponentially faster than classical computers."},
            {"id": 34, "chunk": "Quantum algorithms, such as Shor's algorithm for factoring large numbers, pose a significant challenge to classical encryption methods, influencing cryptographic security."},
            {"id": 56, "chunk": "Quantum tunneling enables certain computing architectures, such as those used in quantum annealers, to solve optimization problems more efficiently."},
            {"id": 78, "chunk": "Advances in quantum mechanics have led to the development of quantum communication, promising ultra-secure data transfer using quantum key distribution."}
        ]
        
        return {
            "precision_at_k": EvaluationService.precision_at_k(
                retrieved_docs=relevant_docs, ground_truth=ground_truth, max_k=top_k
            ),
            
            "recall_at_k": EvaluationService.recall_at_k(
                retrieved_docs=relevant_docs, ground_truth=ground_truth, max_k=top_k
            ),
            
            "f1_score_at_k": EvaluationService.f1_score_at_k(
                retrieved_docs=relevant_docs, ground_truth=ground_truth, max_k=top_k
            ),
            
            "hit_rate_at_k": EvaluationService.hit_rate_at_k(
                retrieved_docs=relevant_docs, ground_truth=ground_truth, max_k=top_k
            ),
            
            "reciprocal_rank": EvaluationService.reciprocal_rank(
                retrieved_docs=relevant_docs, ground_truth=ground_truth
            ),
            
            "ndcg_at_k": EvaluationService.normalized_discounted_cumulative_gain_at_k(
                retrieved_docs=relevant_docs, ground_truth=ground_truth, k=top_k
            ),
            
            "bpref": EvaluationService.bpref(
                retrieved_docs=relevant_docs, ground_truth=ground_truth
            )
        }
            
            
            
            
            
            