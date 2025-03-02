from fastapi import HTTPException

from app.config.database import db_helper
from app.models.domain.indexupsert import IndexUpsert


class IndexUpsertRepository:

    def __init__(self):
        self.collection = db_helper.index_upsert_collection

    async def find_matching_index_upsert(
        self,
        dimension: str,
        similarity_metric: str,
        file_name: str,
        embed_model: str,
    ):
        query = {
            "dimension": dimension,
            "similarity_metric": similarity_metric,
            "namespaces": {
                "$elemMatch": {
                    "details.filename": file_name,
                    "details.embedding_model": embed_model,
                }
            },
        }
        document = await self.collection.find_one(query)
        print(document)
        return document

    async def find_matching_index(self, dimension: str, similarity_metric: str):
        query = {"dimension": dimension, "similarity_metric": similarity_metric}
        document = await self.collection.find_one(query)
        return document

    async def add_index_upsert_details(self, indexupsert: IndexUpsert):
        try:
            # Check if an index with same dimension and similarity_metric exists
            existing_index = await self.collection.find_one(
                {
                    "dimension": indexupsert.dimension,
                    "similarity_metric": indexupsert.similarity_metric,
                }
            )

            if existing_index:
                # Get the first namespace from the new data
                new_namespace = indexupsert.namespaces[0]

                # Check if namespace with same name already exists
                namespace_exists = any(
                    ns["name"] == new_namespace.name
                    for ns in existing_index.get("namespaces", [])
                )

                if namespace_exists:
                    # Namespace already exists, no need to update
                    return str(existing_index["_id"])

                # Add new namespace to existing index
                result = await self.collection.update_one(
                    {"_id": existing_index["_id"]},
                    {
                        "$push": {
                            "namespaces": {
                                "name": new_namespace.name,
                                "details": {
                                    "filename": new_namespace.details.filename,
                                    "embedding_model": new_namespace.details.embedding_model,
                                },
                            }
                        }
                    },
                )
                return str(existing_index["_id"])
            else:
                # Create new index document
                index_upsert_dict = indexupsert.to_dict()
                result = await self.collection.insert_one(index_upsert_dict)
                return str(result.inserted_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
