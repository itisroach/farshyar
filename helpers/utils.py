import logging
import os
import json
from dotenv import load_dotenv
import pathlib


ROOT_DIR = pathlib.Path(__file__).parent.parent

load_dotenv()

def ReadEnvVar(name: str):
    value = os.getenv(name)

    return value


CHANNEL_USERNAME = ReadEnvVar("CHANNEL_USERNAME")


# reading username of channels in file
def ReadChannels(filepath: str):
    
    try:
        file = open(filepath, "r")
        channels = file.read().splitlines()
        return channels
    except Exception as e:
        logging.error(f"Error reading {filepath}: {e}")




class ChannelMessage:

    def __init__(self, client, data):
        self.client  = client
        self.data    = data
        self.caption = f"{data["title"]}\n {data["comb"]} شانه\n {data["details"]}"
        # we convert a json object to a python object
        sizes = json.loads(data["sizes"])
        for size in sizes:
            self.caption += f"\n {size[0]} متری {size[1]} تخته"

    async def SendToChannel(self, images):
        # checks if images is an ablum or not
        if type(images) is list:
            # it will return message id so we can store it in database
            messages = await self.client.send_file(CHANNEL_USERNAME, [os.path.join(ROOT_DIR, "media", image) for image in images], caption=self.caption, force_document=False)
            return json.dumps([message.id for message in messages])
        else:
            message = await self.client.send_message(CHANNEL_USERNAME, self.caption)
            return json.dumps([message.id])
    


    async def EditChannelMessage(self, message_id):
        
        await self.client.edit_message(CHANNEL_USERNAME, message_id, self.caption)