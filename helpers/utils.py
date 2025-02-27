import logging
import json
import os
from dotenv import load_dotenv




load_dotenv()

def ReadEnvVar(name: str):
    value = os.getenv(name)

    return value


CHANNEL_USERNAME=ReadEnvVar("CHANNEL_USERNMAE")


# reading username of channels in file
def ReadChannels(filepath: str):
    
    try:
        file = open(filepath, "r")
        channels = file.read().splitlines()
        return channels
    except Exception as e:
        logging.error(f"Error reading {filepath}: {e}")




async def SendToChannel(client, data):
    caption = f"{data["title"]}\n {data["comb"]} شانه {data["details"]}"
    sizes = json.loads(data["sizes"])
    for size in sizes:
        caption += f"\n {size[0]} متری {size[1]} تخته"


    if type(data["images"]) is list:
        messages = await client.send_file(CHANNEL_USERNAME, data["images"], caption=caption, force_document=False)
        return [message.id for message in messages]
    else:
        message = await client.send_message(CHANNEL_USERNAME, caption)
        return message.id