from telethon import TelegramClient, events, types
from helpers import utils
from db.main import Database
from helpers import messageParser
import asyncio
import os
from helpers import tools
import pytz
import json
from helpers import extractOldMessages
from apscheduler.schedulers.asyncio import AsyncIOScheduler 
from helpers import utils


# telegram credentials
API_ID    = utils.ReadEnvVar("API_ID")
API_HASH  = utils.ReadEnvVar("API_HASH")
BOT_TOKEN = utils.ReadEnvVar("BOT_TOKEN")
SESSION_NAME = utils.ReadEnvVar("SESSION_NAME")

# an instance of telegram client
client = TelegramClient(session=SESSION_NAME, api_id=API_ID, api_hash=API_HASH)


# an instance of database connection
db = Database()

# a function that removes records from database that are not in channels
async def DeleteProduct():
    # getting all product post and channel ids to check for existance in channels
    products = await db.fetch_products_to_remove()

    # a variable that can store image urls to remove from cloud
    records = None

    # iterating over products to gett each product image urls and check for their existance
    for product in products:
        channel_id = int(product["channel_id"])
        message_id = int(product["post_id"])
        

        # check if the message exists in channel
        message_found = await client.get_messages(channel_id, ids=message_id)

        # if message was not found in channel
        if message_found is None:
            channel_id = str(channel_id)
            message_id = str(message_id)
            channel_posts_id = json.loads(product["channel_posts_id"])

            # deleting the product related to message (the query returns images list)
            record = await db.delete_product(channel_id, message_id)

            # deletes posts that has been published in the main channel 
            await client.delete_messages(utils.CHANNEL_USERNAME, channel_posts_id)

            if record is None:
                continue

            if records is None:
                records = record
            else:
                records += record
        
    if records is None:
        return
    
    # deleting image from cloud
    for image in records:
        os.remove(image)
    

    



async def main():
    
    async with client:

        await db.init_db()

        # a scheduler to run every night at 2 am to delete records from database that removed from channels
        scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Tehran"))
        scheduler.add_job(DeleteProduct, "cron", hour=1, minute=15)
        scheduler.start()

        @client.on(events.MessageEdited(chats=["t3362"]))
        async def ListenForEditedMessages(event):
        
            matches = messageParser.ParseMessage(event.text)

            await tools.Create_Data(client, matches, db, event, True)
            
        @client.on(events.NewMessage(chats=["t3362"]))
        async def ListenForMessages(event):
            if "روتین" in event.text:
                return
            # if message contains mutiple images goes out of function
            if event.message.grouped_id:
                return


            # checks if message contains text
            if event.text:
                # geetting  matched from the text
                matches = messageParser.ParseMessage(event.text)

                # checks if message contains only one image 
                if event.message.photo:
                    # runs this procces in background
                    asyncio.create_task(tools.Create_Data(client ,matches, db, event, False, False))

                # add products to database if we don't have image
                else:
                    await tools.Create_Data(client, matches, db, event, False, None)

        # this event happens when multiple images sent
        @client.on(events.Album(chats=["t3362"]))
        async def ListenForImages(event):
            # check if message contains text
            if event.text:
                # finding matches in text
                matches = messageParser.ParseMessage(event.text)
                # uploading file to cloud in the background
                asyncio.create_task(tools.Create_Data(client, matches, db, event, False, True))

                
        await client.run_until_disconnected()



if __name__ == "__main__":
    asyncio.run(main())