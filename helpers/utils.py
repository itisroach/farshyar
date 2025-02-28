import logging
import json
import os
from dotenv import load_dotenv




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




class ChannelMessage():

    def __init__(self, client, data):
        self.client  = client
        self.data    = data
        self.caption = f"{data["title"]}\n {data["comb"]} شانه\n {data["details"]}"
        # we convert a json object to a python object
        sizes = json.loads(data["sizes"])
        for size in sizes:
            self.caption += f"\n {size[0]} متری {size[1]} تخته"

    async def SendToChannel(self):
        # checks if images is an ablum or not
        if type(self.data["images"]) is list:
            # it will return message id so we can store it in database
            messages = await self.client.send_file(CHANNEL_USERNAME, self.data["images"], caption=self.caption, force_document=False)
            return [message.id for message in messages]
        else:
            message = await self.client.send_message(CHANNEL_USERNAME, self.caption)
            return [message.id]
    


    async def EditChannelMessage(self, message_id):
        
        await self.client.edit_message(CHANNEL_USERNAME, message_id, self.caption)