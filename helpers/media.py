from db.main import Database
import datetime
import random
import asyncio
from .utils import ReadEnvVar
from telethon.tl.types import MessageMediaDocument

ROOT_DIR = ReadEnvVar("ROOT_DIR")
db = Database()

async def ProcessImages(event, client, data, isAlbum):
    
    paths = []
    timestamp = datetime.datetime.utcnow()
    # check if it is multiple images 
    if isAlbum:
        # iterating through all images

        if type(event) is list:
            images = event
        else:
            images = event.messages

        for image in images:
        
            if isinstance(image.media , MessageMediaDocument):
                continue
            # genearting unique file name based on ids
            filename = f"{image.chat.id}-{image.id}-{timestamp}.jpg"
            filename = filename.replace(":", "_")
            # uploading file locally on machine
            await asyncio.sleep(random.uniform(1, 3))
            await client.download_media(image, f"{ROOT_DIR}/images/{filename}")
            paths.append(filename)

    # if it's only one image
    else:
        if hasattr(event, "photo"):
            photo = event.photo
            # generating file name based on photo id
            filename = f"{event.chat.id}-{event.id}-{timestamp}.jpg"
        elif hasattr(event.message , "photo"):
            photo = event.message.photo
            # generating file name based on photo id
            filename = f"{event.chat.id}-{event.message.id}-{timestamp}.jpg"
        else:
            return None
        
        filename = filename.replace(":", "_")
        # downloading photo into the machine
        await asyncio.sleep(random.uniform(1, 3))
        await client.download_media(photo, f"{ROOT_DIR}/images/{filename}")
        paths.append(filename)        


    return paths