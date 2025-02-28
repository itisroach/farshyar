import motor.motor_asyncio
from helpers import utils
import motor
import sys

MONGODB_URI=utils.ReadEnvVar("MONGO_DB_URI")


class Database():
    _instance = None
    _initialized = False  # Prevent duplicate init

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.pool = None
            cls._instance.db   = None
            cls._instance.collection = None
            
        return cls._instance

    async def init_db(self):
        # Initialize the database pool if it hasn't been initialized yet.
        if self._initialized:
            return  # Prevent re-initialization
        try:
            self.pool = motor.motor_asyncio.AsyncIOMotorClient()
            self.db   = self.pool.farshyab
            self.collection = self.db.products
            self._initialized = True

        except Exception as e:
            sys.exit(f"Database connection failed: {e}")

        # # Creating table on database connection
        # await self.pool.execute(queries.create_table_query)

    async def fetch_products(self):
        
        return await self.collection.find()

    async def add_products(self, data):
        
        await self.collection.insert_one(data)
        

    async def update_products(self, channel_id, message_id, data):

        result = await self.collection.find_one_and_update(
            filter={"post_id": message_id, "channel_id": channel_id},
            update={"$set": data},
            projection={"channel_posts_id": 1}
        )


        return result["channel_posts_id"]

        
    async def delete_product(self, channel_id, post_id):

        result = await self.collection.find_one_and_delete(
            filter={"channel_id": channel_id, "post_id": post_id},
            projection={"images":1}
        )

        return result
        

    async def fetch_products_to_remove(self):


        result = self.collection.find({}, {"channel_id":1 , "post_id": 1, "channel_posts_id": 1})

        return await result.to_list()