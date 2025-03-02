from fastapi import Depends

from app.models.schemas.reranking_schema import (
    RerankingRequest,
    RerankingResponse,
)
from app.usecases.reranking_usecase import RerankingUseCase


class RerankingController:
    def __init__(self, reranking_usecase: RerankingUseCase = Depends()):
        self.reranking_usecase = reranking_usecase

    async def rerank_documents(
        self, request: RerankingRequest
    ) -> RerankingResponse:
        return await self.reranking_usecase.execute(request)
