from telethon import TelegramClient, events
from helpers import tools
from db.main import Database
from helpers import messageParser
import asyncio
from helpers.cloudStorage import ProcessImages

# telegram credentials
API_ID    = tools.ReadEnvVar("API_ID")
API_HASH  = tools.ReadEnvVar("API_HASH")
BOT_TOKEN = tools.ReadEnvVar("BOT_TOKEN")
SESSION_NAME = tools.ReadEnvVar("SESSION_NAME")

# an instance of database connection
db = Database()

async def main():
    # an instance of telegram client
    client = TelegramClient(session=SESSION_NAME, api_id=API_ID, api_hash=API_HASH)


    async with client:

        await db.init_db()

        @client.on(events.NewMessage())
        async def ListenForMessages(event):
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
                    asyncio.create_task(ProcessImages(event, client, matches, db, False))

                # add products to database if we don't have image
                else:
                    await tools.Create_Data(matches, None, db, event)

        # this event happens when multiple images sent
        @client.on(events.Album())
        async def ListenForImages(event):
            # check if message contains text
            if event.text:
                # finding matches in text
                matches = messageParser.ParseMessage(event.text)
                # uploading file to cloud in the background
                asyncio.create_task(ProcessImages(event, client, matches, db, True))

                
    # starting the bot
    await client.start()
    await client.run_until_disconnected()



if __name__ == "__main__":
    asyncio.run(main())