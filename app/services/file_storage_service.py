import json
import os

class file_storage_service:
    def chunk_and_store(self, json_data: list, chunk_size: int, folder_path: str, base_filename: str):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        chunks = [json_data[i:i + chunk_size] for i in range(0, len(json_data), chunk_size)]
        chunk_paths = []
        for i, chunk in enumerate(chunks):
            chunk_filename = os.path.join(folder_path, f"{base_filename}_chunk_{i}.json")
            with open(chunk_filename, "w") as f:
                json.dump(chunk, f)
            chunk_paths.append(chunk_filename)
        return chunk_paths