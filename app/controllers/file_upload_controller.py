from app.usecases.file_upload_usecase import FileUploadUseCase
from app.models.schemas.file_upload import FileUploadResponse
from fastapi import HTTPException

class FileUploadController:
    def __init__(self, usecase: FileUploadUseCase):
        self.usecase = usecase

    async def upload_files(self, request_data: dict):
        try:
            response_data = self.usecase.execute(request_data)
            return FileUploadResponse(
                data=response_data,
                statuscode=200,
                detail="Files uploaded successfully",
                error=""
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=FileUploadResponse(
                    data={},
                    statuscode=500,
                    detail="File upload failed",
                    error=str(e)
                ).dict()
            )