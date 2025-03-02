from fastapi import Depends

from app.usecases.index_upsert_usecase import IndexUpsertUseCase


class IndexUpsertController:
    def __init__(self, index_upsert_usecase=Depends(IndexUpsertUseCase)):
        self.index_upsert_usecase = index_upsert_usecase

    async def index_upsert(self, request):

        return await self.index_upsert_usecase.index_upsert(request)
        dimension = request.dimension
        similarity_metric = request.similarity_metric
        file_name = request.file_name
        embed_model = request.embed_model

        already_upserted = (
            await self.index_upsert_repository.find_matching_index_upsert(
                dimension, similarity_metric, file_name, embed_model
            )
        )

        if already_upserted:
            return "such dimension, similarity metric, filename and embed model configuration already exists, move on to query"

        already_index = await self.index_upsert_repository.find_matching_index(
            dimension, similarity_metric
        )

        return await self.index_upsert_usecase.index_upsert(
            request, already_index
        )
