from pydantic import BaseModel

class FileUploadRequest(BaseModel):
    input_data: str
    ground_truth: str