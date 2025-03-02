from app.usecases.query_usecase import QueryUseCase
from fastapi import Depends, status, HTTPException
from app.models.schemas.query_schema import QueryEndPointRequest
from fastapi.responses import JSONResponse

class QueryController:
    
    def __init__(self, usecase: QueryUseCase = Depends()):
        self.query_usecase = usecase
        
    async def make_query(self, request: QueryEndPointRequest):
        try:    
            response_data = await self.query_usecase.execute(request)
            
            return JSONResponse(
                content = {
                    "data": response_data,
                    "statuscode": 200,
                    "detail": "Query execution successful!",
                    "error": ""
                    },
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "data": {},
                    "statuscode": 500,
                    "detail": "Query execution failed!",
                    "error": str(e)
                }
            )
        