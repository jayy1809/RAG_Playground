from fastapi import Depends, HTTPException

from app.models.schemas.reranking_schema import (
    RerankingRequest,
    RerankingResponse,
    RerankingResult,
)
from app.repositories.index_repository import IndexRepository
from app.services.evaluation_service import EvaluationService
from app.services.reranking_service import RerankerService


class RerankingUseCase:
    def __init__(
        self,
        index_repository: IndexRepository = Depends(),
        reranker_service: RerankerService = Depends(),
    ):
        self.reranker_service = reranker_service
        self.index_repository = index_repository

    async def execute(self, request: RerankingRequest) -> RerankingResponse:
        """
        Execute the reranking use case

        Args:
            model_name: Name of the reranking model to use
            query: The search query
            documents: List of documents to rerank
            top_n: Number of top results to return

        Returns:
            Reranking response with results
        """
        try:

            documents = request.documents
            model_name = request.model_name
            query = request.query
            top_n = request.top_n

            pinecone_models = [
                "cohere-rerank-3.5",
                "bge-reranker-v2-m3",
                "pinecone-rerank-v0",
            ]
            cohere_models = [
                "rerank-v3.5",
                "rerank-english-v3.0",
                "rerank-multilingual-v3.0",
            ]
            jina_models = ["jina-reranker-v2-base-multilingual"]
            docs = [doc["text"] for doc in documents]
            # Determine which reranker to use based on the model name
            if model_name.lower() in pinecone_models:
                p_docs = [{"text": doc["text"]} for doc in documents]
                reranking_result = (
                    await self.reranker_service.pinecone_reranker(
                        model_name, query, p_docs, top_n
                    )
                )
                results = []
                for result in reranking_result.get("data", []):
                    results.append(
                        RerankingResult(
                            document=result.get("document", ""),
                            score=result.get("score", 0.0),
                        )
                    )

            elif model_name.lower() in cohere_models:
                reranking_result = await self.reranker_service.cohere_rerank(
                    model_name, query, docs, top_n
                )
                results = []
                for result in reranking_result.get("results", []):
                    results.append(
                        RerankingResult(
                            document=documents[result.get("index", "")],
                            score=result.get("relevance_score", 0.0),
                        )
                    )
            elif model_name.lower() in jina_models:
                reranking_result = await self.reranker_service.jina_rerank(
                    model_name, query, docs, top_n
                )
                results = []
                for result in reranking_result.get("results", []):
                    results.append(
                        RerankingResult(
                            document=documents[result.get("index", "")],
                            score=result.get("relevance_score", 0.0),
                        )
                    )

            else:
                # Default to Pinecone
                model = "bge-reranker-v2-m3"
                reranking_result = (
                    await self.reranker_service.pinecone_reranker(
                        model, query, p_docs, top_n
                    )
                )

                # Transform the reranking service response to match our schema
                results = []
                for result in reranking_result.get("results", []):
                    results.append(
                        RerankingResult(
                            document=result.get("document", ""),
                            score=result.get("score", 0.0),
                        )
                    )

            ground_truth = await self._get_ground_truth(query)

            if not results:
                return {"results": {}, "error": "No relevant documents found."}

            if not ground_truth:
                return {
                    "results": results,
                    "error": "No ground truth data found. please enter a valid query to get the evaluation metrics.",
                }

            evaluation_metrics = self._calculate_evaluation_metrics(
                results, ground_truth, top_n
            )

            return RerankingResponse(
                results=results, evaluation_metrics=evaluation_metrics
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_ground_truth(self, query):
        """Fetch ground truth data for the query."""

        return await self.index_repository.fetch_ground_truth(query=query)

    def _calculate_evaluation_metrics(self, relevant_docs, ground_truth, top_n):
        """Calculate various evaluation metrics for the search results."""

        dummy_ground_truth = [
            {
                "id": 12,
                "chunk": "Quantum mechanics provides the foundation for quantum computing, leveraging superposition and entanglement to process information exponentially faster than classical computers.",
            },
            {
                "id": 34,
                "chunk": "Quantum algorithms, such as Shor's algorithm for factoring large numbers, pose a significant challenge to classical encryption methods, influencing cryptographic security.",
            },
            {
                "id": 56,
                "chunk": "Quantum tunneling enables certain computing architectures, such as those used in quantum annealers, to solve optimization problems more efficiently.",
            },
            {
                "id": 78,
                "chunk": "Advances in quantum mechanics have led to the development of quantum communication, promising ultra-secure data transfer using quantum key distribution.",
            },
        ]

        return {
            "precision_at_k": EvaluationService.precision_at_k(
                retrieved_docs=relevant_docs,
                ground_truth=ground_truth,
                max_k=top_n,
            ),
            "recall_at_k": EvaluationService.recall_at_k(
                retrieved_docs=relevant_docs,
                ground_truth=ground_truth,
                max_k=top_n,
            ),
            "f1_score_at_k": EvaluationService.f1_score_at_k(
                retrieved_docs=relevant_docs,
                ground_truth=ground_truth,
                max_k=top_n,
            ),
            "hit_rate_at_k": EvaluationService.hit_rate_at_k(
                retrieved_docs=relevant_docs,
                ground_truth=ground_truth,
                max_k=top_n,
            ),
            "reciprocal_rank": EvaluationService.reciprocal_rank(
                retrieved_docs=relevant_docs, ground_truth=ground_truth
            ),
            "ndcg_at_k": EvaluationService.normalized_discounted_cumulative_gain_at_k(
                retrieved_docs=relevant_docs, ground_truth=ground_truth, k=top_n
            ),
            "bpref": EvaluationService.bpref(
                retrieved_docs=relevant_docs, ground_truth=ground_truth
            ),
        }
