from fastapi import APIRouter, Depends, status
from app.models.schemas.index_upsert_schema import IndexUpsertRequest
from app.controllers.index_upsert_controller import IndexUpsertController
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/index-upsert")
async def index_upsert(
    request: IndexUpsertRequest,
    index_upsert_controller : IndexUpsertController = Depends(IndexUpsertController),
    ):

    response = await index_upsert_controller.index_upsert(request)

    return JSONResponse(
        content = {
            "data" : {"host": response},
            "status_code" : status.HTTP_200_OK,
            "detail" : "Upserted Successfully",
            "error" : ""
        },
        status_code = status.HTTP_200_OK
    )