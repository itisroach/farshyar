from helpers import utils
import aiomysql
import sys
from . import queries

DBConfig = {
    "user": utils.ReadEnvVar("DB_USER"),
    "password": utils.ReadEnvVar("DB_PASS"),
    "host": "localhost",
    "db": utils.ReadEnvVar("DB_NAME"),
    "minsize": 1,
    "maxsize": 30
}


class Database():
    _instance = None
    _initialized = False  # Prevent duplicate init

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.pool = None
            
        return cls._instance

    async def init_db(self):
        # Initialize the database pool if it hasn't been initialized yet.
        if self._initialized:
            return  # Prevent re-initialization
        try:
            self.pool = await aiomysql.create_pool(**DBConfig)
            self._initialized = True

        except Exception as e:
            sys.exit(f"Database connection failed: {e}")

        # Creating table on database connection
        await self.create_table()

    async def create_table(self):
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cur:
                await cur.execute(queries.create_table_query)
                await cur.execute(queries.create_images_table_query)
                await connection.commit()

    async def fetch_products(self):
        # Fetch products from database
        if self.pool is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(queries.fetch_items_query)
                return await cur.fetchall()
        
    async def add_products(self, *args):
        
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cur:
                await cur.execute(queries.insert_item_query, args)

                inserted_id = cur.lastrowid

                await connection.commit()

                return inserted_id

    async def update_products(self, channel_id, message_id, *args):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(queries.update_item_query, (*args, channel_id, message_id))              
                await connection.commit()
        
    async def delete_product(self, channel_id, post_id):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(queries.fetch_images_to_remove, (post_id, channel_id))

                result = []

                for row in await cur.fetchall():
                    if "filename" in row:
                        result.append(row["filename"])
                    else:
                        result = None

                await cur.execute(queries.delete_item_query, (channel_id, post_id)) 
                await connection.commit()
                return result

    async def fetch_products_to_remove(self):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(queries.fetch_items_to_remove)
                return await cur.fetchall()
        

    async def add_images(self, inserted_id, images: list):
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cur:
                for image in images:
                    await cur.execute(queries.insert_images_query, (inserted_id, image))
                await connection.commit()

    async def close_pool(self):
        self.pool.close()
        await self.pool.wait_closed()