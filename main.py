import asyncio
from telethon import TelegramClient, events
from helpers import utils
from db.main import Database
from helpers import messageParser, tools
import os
import random
import pytz
from helpers import extractOldMessages
from apscheduler.schedulers.asyncio import AsyncIOScheduler 
from telethon.tl.types import MessageMediaDocument

# Telegram credentials
API_ID = utils.ReadEnvVar("API_ID")
API_HASH = utils.ReadEnvVar("API_HASH")
BOT_TOKEN = utils.ReadEnvVar("BOT_TOKEN")
SESSION_NAME = utils.ReadEnvVar("SESSION_NAME")
ROOT_DIR = utils.ReadEnvVar("ROOT_DIR")
CHANNELS_NAME_FILE = utils.ReadEnvVar("CHANNELS_NAME_FILE")


# Database instance
db = Database()

# Read channels from file
channels_to_look_for = utils.ReadChannels("/home/farshya1/python_bot/farshyab.txt")
for idx, channel in enumerate(channels_to_look_for):
    channels_to_look_for[idx] = channel.split()[0]


async def DeleteProduct(client):
    # Delete records from the database that are not in the Telegram channel.
    products = await db.fetch_products_to_remove()
    records = None

    for product in products:
        channel_id = int(product["channel_id"])
        message_id = int(product["post_id"])
        await asyncio.sleep(random.uniform(2, 4))
        # Check if the message exists in the channel
        message_found = await client.get_messages(channel_id, ids=message_id)

        if message_found is None:
            channel_id = str(channel_id)
            message_id = str(message_id)

            # Delete product record
            record = await db.delete_product(channel_id, message_id)
            if record:
                records = record if records is None else records + record

    if records:
        for image in records:
            os.remove(os.path.join(ROOT_DIR, "images", image))


async def main():
    await db.init_db()
    # Create the client instance
    client = await TelegramClient(SESSION_NAME, API_ID, API_HASH).start()
    
    async def DeleteProductExecuter():
        await DeleteProduct(client)
    
    await extractOldMessages.JoinChannels(client, CHANNELS_NAME_FILE)

    # Scheduler to delete products at 1:15 AM
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Tehran"))
    scheduler.add_job(DeleteProductExecuter, "cron", hour=2, minute=0)
    scheduler.start()

    @client.on(events.MessageEdited(chats=channels_to_look_for))
    async def ListenForEditedMessages(event):
        if "روتین" in event.text or "فروخته"in event.text or "فروش"  in event.text:
                            return
        matches = messageParser.ParseMessage(event.text)
        await tools.Create_Data(client, matches, db, event, True)

    @client.on(events.Album(chats=channels_to_look_for))
    async def ListenForImages(event):
        
        await asyncio.sleep(random.uniform(2, 4))
        matches = messageParser.ParseMessage(event.text)
        asyncio.create_task(tools.Create_Data(client, matches, db, event, False, True))


    @client.on(events.NewMessage(chats=channels_to_look_for))
    async def ListenForMessages(event):
        if event.message.grouped_id:  # Ignore grouped images
            return
        
        await asyncio.sleep(random.uniform(2, 4))
        if "روتین" in event.text:
            return
        
        matches = messageParser.ParseMessage(event.text)
        if hasattr(event, "media") and isinstance(event.media, MessageMediaDocument):
            return
        if event.message.photo:
            asyncio.create_task(tools.Create_Data(client, matches, db, event, False, False))

    
    # Start the client properly
    async with client:
        await client.run_until_disconnected()


# Fix the event loop handling
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
