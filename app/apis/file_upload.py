from fastapi import APIRouter, Depends

from app.controllers.file_upload_controller import FileUploadController
from app.models.schemas.file_upload import FileUploadRequest

router = APIRouter()


@router.post("/upload-files")
async def upload_files(
    request: FileUploadRequest,
    file_controller: FileUploadController = Depends(),
):
    return await file_controller.upload_files(request.model_dump())
