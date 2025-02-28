import json
from app.services.file_storage_service import file_storage_service

class FileUploadUseCase:
    def __init__(self, storage_service: file_storage_service):
        self.storage_service = storage_service

    def execute(self, request_data: dict):
        input_data_str = request_data["input_data"]
        ground_truth_str = request_data["ground_truth"]

        input_data = json.loads(input_data_str)
        ground_truth = json.loads(ground_truth_str)

        if not isinstance(input_data, list) or not isinstance(ground_truth, list):
            raise ValueError("JSON data must be a list")

        folder_path = "uploaded_files"
        input_chunks_paths = self.storage_service.chunk_and_store(input_data, 1000, folder_path, "input_data")
        ground_truth_chunks_paths = self.storage_service.chunk_and_store(ground_truth, 1000, folder_path, "ground_truth")

        return {
            "input_chunks": input_chunks_paths,
            "ground_truth_chunks": ground_truth_chunks_paths
        }