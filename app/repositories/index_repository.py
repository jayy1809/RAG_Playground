from app.config.database import db_helper

class IndexRepository:
    def __init__(self):
        self.ground_truth_collection = db_helper.gt_data
        self.raw_collection = db_helper.raw_data
        self.index_info_collection = db_helper.index_upsert_collection
        
    async def fetch_ground_truth(self, query):
        
        query = {
            "question" : query
        }
        
        ground_truth_doc = await self.ground_truth_collection.find_one(query)
        
        ground_truth_ids = []
        for x in ground_truth_doc["chunks"]:
            ground_truth_ids.append(x["_id"])
            
        ground_truth = []
        for _id in ground_truth_ids:
            chunk = await self.raw_collection.find_one({"_id" : _id})
            
            ground_truth.append(
                {
                    "id" : _id,
                    "chunk" : chunk["text_content"]
                }
            )
        
        return ground_truth
            
    async def get_namespace_and_host(self, index_name: str, embedding_model: str, filename: str):
        
        query = {
            "index_name": index_name,
            "namespaces": {
                "$elemMatch": {
                    "details.filename": filename,
                    "details.embedding_model": embedding_model
                }
            }
        }
        
        document = await self.index_info_collection.find_one(query)
        namespace = document.get("namespaces", [])[0]
        namespace_name = namespace.get("name", None)
        host = document.get("index_host")
        
        return namespace_name, host
        