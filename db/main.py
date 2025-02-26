from helpers import tools
import asyncpg
import sys
from . import queries

DBConfig = {
    "user": tools.ReadEnvVar("DB_USER"),
    "password": tools.ReadEnvVar("DB_PASS"),
    "host": tools.ReadEnvVar("DB_HOST"),
    "database": tools.ReadEnvVar("DB_NAME"),
    "port": tools.ReadEnvVar("DB_PORT"),
    "server_settings": {"client_encoding": "UTF8"}
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
            self.pool = await asyncpg.create_pool(**DBConfig)
            self._initialized = True

        except Exception as e:
            sys.exit(f"Database connection failed: {e}")

        # Creating table on database connection
        await self.pool.execute(queries.create_table_query)

    async def fetch_products(self):
        # Fetch products from database
        if self.pool is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        async with self.pool.acquire() as connection:
            return await connection.fetch(queries.fetch_items_query)
        
    async def add_products(self, *args):
        
        async with self.pool.acquire() as connection:
            return await connection.execute(queries.insert_item_query, *args)
        

    async def update_products(self, channel_id, message_id, *args):
        async with self.pool.acquire() as connection:
            print(*args, channel_id, message_id)
            return await connection.execute(queries.update_item_query, *args, channel_id, message_id)
        
    async def delete_product(self, channel_id, post_id):
        async with self.pool.acquire() as connection:
            return await connection.execute(queries.delete_item_query, channel_id, post_id) 
        

    async def fetch_products_to_remove(self):
        async with self.pool.acquire() as connection:
            return await connection.fetch(queries.fetch_items_to_remove)