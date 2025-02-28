import json
from app.utils.file_utils import FileUtils
from app.config.settings import Settings
from fastapi import Depends

class FileUploadUseCase:
    def __init__(self, storage_utils: FileUtils = Depends()):
        self.storage_utils = storage_utils
        self.settings = Settings()

    def execute(self, request_data: dict):
        input_data_str = request_data["input_data"]

        input_data = json.loads(input_data_str)

        if not isinstance(input_data, list):
            raise ValueError("JSON data must be a list")

        folder_path = self.settings.GROUND_TRUTH_FILE_STORE_PATH
        input_chunks_paths = self.storage_utils.chunk_and_store(input_data, self.settings.GROUND_TRUTH_CHUNK_SIZE, folder_path, self.settings.GROUND_TRUTH_FILE_BASE_NAME)

        return {
            "input_chunks": input_chunks_paths
        }