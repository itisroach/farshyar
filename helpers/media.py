import asyncio
import os
from db.main import Database
from .utils import ChannelMessage


db = Database()

async def ProcessImages(event, client, data, isAlbum):
    
    paths = []

    # check if it is multiple images 
    if isAlbum:
        # iterating through all images

        if type(event) is list:
            images = event
        else:
            images = event.messages

        for image in images:
            # genearting unique file name based on ids
            filename = f"{image.chat.id}-{image.id}.jpg"
            # uploading file locally on machine
            file_path = await client.download_media(image, f"./media/{filename}")

            paths.append(file_path)

    # if it's only one image
    else:
        photo = event.message.photo

        # generating file name based on photo id
        filename = f"{event.chat.id}-{event.message.id}.jpg"
        # downloading photo into the machine
        file_path = await client.download_media(photo, f"./media/{filename}")
        paths.append(file_path)        

    

    # sending message to channel
    data["images"] = paths

    channel_message = ChannelMessage(client, data)

    message_ids = await channel_message.SendToChannel()
    # adding post ids in database so it can be accessable 
    data["channel_posts_id"] = message_ids

    return paths

def RemoveImages(filepaths):
    for path in  filepaths:
        os.remove(path)