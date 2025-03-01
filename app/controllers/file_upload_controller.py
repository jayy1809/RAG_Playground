from app.usecases.file_upload_usecase import FileUploadUseCase
from fastapi import HTTPException, Depends, status
from fastapi.responses import JSONResponse

class FileUploadController:
    def __init__(self, usecase: FileUploadUseCase = Depends()):
        self.usecase = usecase

    async def upload_files(self, request_data: dict):
        try:
            response_data = await self.usecase.execute(request_data)
            return JSONResponse(
                content = {
                    "data": response_data,
                    "statuscode": 200,
                    "detail": "File uploaded successfully",
                    "error": ""
                },
                status_code=status.HTTP_200_OK
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "data": {},
                    "statuscode": 500,
                    "detail": "File upload failed",
                    "error": str(e)
                }
            )