from app.usecases.file_upload_usecase import FileUploadUseCase
from fastapi import HTTPException, Depends, status
from fastapi.responses import JSONResponse
from app.config.database import db_helper
from app.models.domain.indexupsert import IndexUpsert



class IndexUpsertRepository:

    def __init__(self):
        self.collection = db_helper.index_upsert_collection


    async def find_matching_index_upsert(self, dimension:str, similarity_metric: str, file_name: str, embed_model: str):
        query = {
            "dimension": dimension,
            "similarity_metric": similarity_metric,
            "namespaces": {
                "$elemMatch": {
                    "details.filename": file_name,
                    "details.embedding_model": embed_model
                }
            }
        }
        document = await self.collection.find_one(query)
        print(document)
        return document

    async def find_matching_index(self, dimension:str, similarity_metric: str):
        query = {
            "dimension": dimension,
            "similarity_metric": similarity_metric
        }
        document = await self.collection.find_one(query)
        return document

    async def add_index_upsert_details(self, indexupsert: IndexUpsert):
        try:
            index_upsert_dict = indexupsert.to_dict()
            result = await self.collection.insert_one(index_upsert_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))