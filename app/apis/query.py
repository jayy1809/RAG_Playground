from fastapi import APIRouter, Depends
from app.controllers.query_controller import QueryController
from app.models.schemas.query_schema import QueryEndPointRequest

router = APIRouter()

@router.post("/query")
async def make_query(request: QueryEndPointRequest, query_controller: QueryController = Depends()):
    return await query_controller.make_query(request)