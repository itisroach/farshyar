from telethon import TelegramClient, events
from helpers import tools
from helpers import messageParser

API_ID    = tools.ReadEnvVar("API_ID")
API_HASH  = tools.ReadEnvVar("API_HASH")
BOT_TOKEN = tools.ReadEnvVar("BOT_TOKEN")
SESSION_NAME = tools.ReadEnvVar("SESSION_NAME")



client = TelegramClient(session=SESSION_NAME, api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)



@client.on(events.NewMessage())
async def ListenForMessages(event):
    if event.text:
        messageParser.ParseMessage(event.text)


client.start()
client.run_until_disconnected()