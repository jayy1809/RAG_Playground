from fastapi import Depends

from app.models.schemas.query_schema import QueryEndPointRequest
from app.usecases.query_usecase import QueryUseCase


class QueryController:

    def __init__(self, usecase: QueryUseCase = Depends()):
        self.query_usecase = usecase

    async def make_query(self, request: QueryEndPointRequest):
        return await self.query_usecase.execute(request)
