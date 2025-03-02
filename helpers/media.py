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

    
    # a class for accessing channel and publishing posts in it
    channel_message = ChannelMessage(client, data)
    message_ids = await channel_message.SendToChannel(paths)

    # adding post ids in database so it can be accessable 
    data["channel_posts_id"] = message_ids

    return paths

