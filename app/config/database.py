from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

class DBHelper:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
        self.raw_data = self.db["raw_data"]
        self.gt_data = self.db["gt_data"]

    async def connect(self):
        try:
            if self.client is None:
                self.client = AsyncIOMotorClient(
                    settings.MONGODB_URL,
                    maxPoolSize=1000,
                    minPoolSize=50,
                    maxIdleTimeMS=50000,
                    connectTimeoutMS=20000,
                )
                
                self.db = self.client[settings.DATABASE_NAME]
                await self.client.admin.command('ping')
                await self.create_collections()

        except Exception as e:
            if self.client:
                await self.disconnect()
            raise

    async def create_collections(self):
        required_collections = ["raw_data", "gt_data"]
        existing_collections = await self.db.list_collection_names()
        for collection in required_collections:
            if collection not in existing_collections:
                await self.db.create_collection(collection)

    async def get_db(self):
        if self.client is None:
            await self.connect()
        return self.db

    async def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

db_helper = DBHelper()