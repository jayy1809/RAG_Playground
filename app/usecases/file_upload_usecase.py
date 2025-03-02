import asyncio
import json
import os
import random
from uuid import uuid4

import aiofiles

from app.config.settings import settings
from app.repositories.gt_data_repo import GTDataRepo
from app.repositories.raw_data_repo import RawDataRepo
from app.utils.llm_utils import LLMUtils


class FileUploadUseCase:
    def __init__(self):
        self.raw_data_repo = RawDataRepo()
        self.gt_data_repo = GTDataRepo()
        self.llm_utils = LLMUtils()

    async def store_file_locally(self, file):
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, "raw_dataset.json")
        async with aiofiles.open(file_path, "w") as f:
            await f.write(file)
        return file_path

    async def process_and_enrich_json(self, file_path):
        async with aiofiles.open(file_path, "r") as f:
            content = await f.read()
            data = json.loads(content)
        if not isinstance(data, list):
            raise ValueError("JSON data must be a list")
        enriched_data = []
        for item in data:
            item["_id"] = str(uuid4())
            enriched_data.append(item)
        async with aiofiles.open(file_path, "w") as f:
            await f.write(json.dumps(enriched_data))
        return enriched_data

    async def process_single_chunk(self, chunk):
        chunk_text = json.dumps(chunk)
        questions = await self.llm_utils.generate_questions(chunk_text)
        chunk_ref = {
            "_id": chunk["_id"],
            "keyword": chunk["keyword"],
            "link": chunk["link"],
        }
        return [{"question": q, "chunks": [chunk_ref]} for q in questions]

    async def process_multi_chunk(self, chunks):
        print(f"Input chunks type: {type(chunks)}")
        print(f"First chunk type: {type(chunks[0]) if chunks else 'No chunks'}")

        chunk_data_for_llm = []
        for chunk in chunks:
            if "text" not in chunk:
                print(f"Warning: 'text' field missing in chunk: {chunk.keys()}")
                text = (
                    chunk.get("content", "")
                    or chunk.get("body", "")
                    or str(chunk)
                )
            else:
                text = chunk["text"]

        chunk_data_for_llm.append(
            {"text": chunk["text"], "_id": chunk["_id"]} for chunk in chunks
        )

        chunk_refs = [
            {
                "_id": chunk["_id"],
                "keyword": chunk["keyword"],
                "link": chunk["link"],
            }
            for chunk in chunks
        ]
        print(
            f"Prepared chunk_data_for_llm: {chunk_data_for_llm[0] if chunk_data_for_llm else 'Empty'}"
        )

        response_json = await self.llm_utils.generate_multi_chunk_question(
            chunk_data_for_llm
        )

        print(f"LLM response type: {type(response)}")
        print(f"LLM response: {response}")
        if isinstance(response_json, str):
            response = json.loads(response_json)
        else:
            response = response_json

        question, relevant_ids = response["question"], response["relevant_ids"]

        relevant_chunks = [
            ref for ref in chunk_refs if ref["_id"] in relevant_ids
        ]
        return [{"question": question, "chunks": relevant_chunks}]

    async def generate_single_chunk_queries(self, chunks_with_metadata):
        dataset = []
        tasks = []
        for item in chunks_with_metadata:
            task = self.process_single_chunk(item)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        for result in results:
            dataset.extend(result)
        return dataset

    async def generate_multi_chunk_queries(self, chunks_with_metadata):
        dataset = []
        tasks = []
        for _ in range(settings.MULTI_CHUNK_QUERIES_COUNT):
            num_chunks = random.randint(
                settings.MIN_CHUNKS_FOR_MULTI_QUERY,
                settings.MAX_CHUNKS_FOR_MULTI_QUERY,
            )
            selected_items = random.sample(
                chunks_with_metadata, min(num_chunks, len(chunks_with_metadata))
            )
            task = self.process_multi_chunk(list(selected_items))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        for result in results:
            dataset.extend(result)
        return dataset

    async def execute(self, request_data):
        try:

            # File Store
            file = request_data.get("input_data")
            if not isinstance(file, str):
                raise ValueError("Input data must be a string")
            file_path = await self.store_file_locally(file)
            enriched_data = await self.process_and_enrich_json(file_path)
            await self.raw_data_repo.clear_collection()
            await self.raw_data_repo.insert_documents(enriched_data)

            # Generate Queries
            single_chunk_dataset = await self.generate_single_chunk_queries(
                enriched_data
            )
            # multi_chunk_dataset = await self.generate_multi_chunk_queries(enriched_data)
            complete_dataset = single_chunk_dataset
            # complete_dataset = multi_chunk_dataset
            # complete_dataset = single_chunk_dataset + multi_chunk_dataset

            # Prepare dataset for MongoDB by removing or regenerating _id fields
            mongo_dataset = []
            for item in complete_dataset:
                new_item = item.copy()
                if "_id" in new_item:
                    del new_item["_id"]
                mongo_dataset.append(new_item)

            await self.gt_data_repo.clear_collection()
            await self.gt_data_repo.insert_documents(mongo_dataset)

            dataset_path = os.path.join(settings.UPLOAD_DIR, "rag_dataset.json")
            async with aiofiles.open(dataset_path, "w") as f:
                await f.write(json.dumps(complete_dataset))

            return {"data": "File processed and dataset generated successfully"}
        except Exception as e:
            raise Exception(str(e))
