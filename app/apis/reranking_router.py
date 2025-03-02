from fastapi import APIRouter, Body, Depends

from app.controllers.reranking_controller import RerankingController
from app.models.schemas.reranking_schema import (
    RerankingRequest,
    RerankingResponse,
)

router = APIRouter(tags=["reranking"])


@router.post("/rerank", response_model=RerankingResponse)
async def rerank_documents(
    request: RerankingRequest = Body(...),
    controller: RerankingController = Depends(),
):
    return await controller.rerank_documents(request)
