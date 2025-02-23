from telethon import TelegramClient, events
from helpers import tools
from db.main import Database
from helpers import messageParser
import asyncio

API_ID    = tools.ReadEnvVar("API_ID")
API_HASH  = tools.ReadEnvVar("API_HASH")
BOT_TOKEN = tools.ReadEnvVar("BOT_TOKEN")
SESSION_NAME = tools.ReadEnvVar("SESSION_NAME")

db = Database()

async def main():
    client = await TelegramClient(session=SESSION_NAME, api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)

    async with client:

        await db.init_db()

        @client.on(events.NewMessage())
        async def ListenForMessages(event):
            if event.text:
                data = messageParser.ParseMessage(event.text)
                # add products to database
                await db.add_products(*data.values())


    await client.start()
    await client.run_until_disconnected()



if __name__ == "__main__":
    asyncio.run(main())