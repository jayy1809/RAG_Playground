from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.controllers.query_controller import QueryController
from app.models.schemas.query_schema import QueryEndPointRequest

router = APIRouter()


@router.post("/query")
async def make_query(
    request: QueryEndPointRequest, query_controller: QueryController = Depends()
):
    try:
        response_data = await query_controller.make_query(request)

        return JSONResponse(
            content={
                "data": response_data,
                "statuscode": 200,
                "detail": "Query execution successful!",
                "error": "",
            },
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "data": {},
                "statuscode": 500,
                "detail": "Query execution failed!",
                "error": str(e),
            },
        )
