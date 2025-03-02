from app.config.database import db_helper


class GTDataRepo:
    def __init__(self):
        self.collection = db_helper.gt_data

    async def clear_collection(self):
        await self.collection.delete_many({})

    async def insert_documents(self, documents: list):
        await self.collection.insert_many(documents)
