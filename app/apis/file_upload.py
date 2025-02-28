from fastapi import APIRouter, Depends
from app.controllers.file_upload_controller import FileUploadController
from models.schemas import FileUploadRequest, FileUploadResponse
from app.utils.dependency_injection import get_file_upload_controller

router = APIRouter()

@router.post("/upload-files", response_model=FileUploadResponse)
async def upload_files(request: FileUploadRequest, controller: FileUploadController = Depends(get_file_upload_controller)):
    return await controller.upload_files(request.dict())