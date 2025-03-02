from fastapi.responses import JSONResponse
from fastapi import Depends, HTTPException, status

from app.usecases.query_usecase import QueryUseCase
from app.models.schemas.query_schema import QueryEndPointRequest


class QueryController:

    def __init__(self, usecase: QueryUseCase = Depends()):
        self.query_usecase = usecase

    async def make_query(self, request: QueryEndPointRequest):
        return await self.query_usecase.execute(request)