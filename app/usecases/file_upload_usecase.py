import json
from app.utils.file_utils import FileUtils
from app.utils.llm_utills import LLMUtils
from app.config.settings import Settings
from fastapi import Depends

class FileUploadUseCase:
    def __init__(self, storage_utils: FileUtils = Depends(), llm_utils: LLMUtils = Depends()):
        self.storage_utils = storage_utils
        self.llm_utils = llm_utils
        self.settings = Settings()

    def chunk_text(self, text, chunk_size=512, overlap=64):
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - overlap)]

    def execute(self, request_data: dict):
        input_data_str = request_data["input_data"]

        input_data = json.loads(input_data_str)

        if not isinstance(input_data, list):
            raise ValueError("JSON data must be a list")

        folder_path = self.settings.GROUND_TRUTH_FILE_STORE_PATH
        input_chunks_paths = self.storage_utils.chunk_and_store(input_data, self.settings.GROUND_TRUTH_CHUNK_SIZE, folder_path, self.settings.GROUND_TRUTH_FILE_BASE_NAME)

        dataset = []
        for chunk_path in input_chunks_paths:
            with open(chunk_path, 'r') as f:
                chunk_data = json.load(f)
                for item in chunk_data:
                    # Error is here - incorrect self reference in the method call
                    # Original: chunks = self.chunk_text(self, item.get("text_content", ""))
                    # Fixed version:
                    text_content = item.get("text_content", "")
                    if text_content:
                        chunks = self.chunk_text(text_content)
                        for chunk in chunks:
                            questions = self.llm_utils.generate_questions(chunk)
                            for question in questions:
                                dataset.append({
                                    'query': question,
                                    'ground_truth': chunk,
                                    'source': item.get('link', '')
                                })

        # dataset = []
        # for chunk_path in input_chunks_paths:
        #     with open(chunk_path, 'r') as f:
        #         chunk_data = json.load(f)
        #         for item in chunk_data:
        #             chunks = self.chunk_text(self, item.get("text_content", ""))
        #             for chunk in chunks:
        #                 questions = self.llm_utils.generate_questions(chunk)
        #                 for question in questions:
        #                     dataset.append({
        #                         'query': question,
        #                         'ground_truth': chunk,
        #                         'source': item['link']
        #                     })
                    # if text_content:
                    #     questions = self.llm_utils.generate_questions(text_content)
                    #     for question in questions:
                    #         dataset.append({
                    #             "query": question,
                    #             "ground_truth": text_content,
                    #             "source": item.get("link", "")
                    #         })

        dataset_path = f"{folder_path}/rag_dataset.json"
        with open(dataset_path, "w") as f:
            json.dump(dataset, f)

        return {
            "input_chunks": input_chunks_paths
        }