from helpers import tools
import asyncpg
import sys
import queries

DBConfig = {
    "user": tools.ReadEnvVar("USER_DB"),
    "password": tools.ReadEnvVar("PASS_DB"),
    "host": tools.ReadEnvVar("HOST_DB"),
    "database": tools.ReadEnvVar("DB_NAME"),
    "port": tools.ReadEnvVar("DB_PORT"),
    "server_settings": {"client_encoding": "UTF8"}
}


class Database():
    _instance = None


    def __init__(self):
        if self._instance is None:
            self._instance = super(Database, self).__new__(self)
    

    async def init_db(self):
        try:
            self.pool = await asyncpg.create_pool(**DBConfig)
        except Exception as e:
            sys.exit(e)

        # creating table on database connection
        await self.pool.execute(queries.create_table_query)


    async def fetch_products(self):
        async with self.pool.acquire() as connection:
            return await connection.fetch(queries.fetch_items_query)