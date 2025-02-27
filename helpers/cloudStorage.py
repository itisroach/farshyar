import boto3 
import asyncio
import os
from db.main import Database
from .utils import ReadEnvVar, SendToChannel
import logging

# cloud credentials
CLOUD_ENDPOINT   = ReadEnvVar("CLOUD_ENDPOINT")
CLOUD_ACCESS_KEY = ReadEnvVar("CLOUD_ACCESS_KEY")
CLOUD_SECRET_KEY = ReadEnvVar("CLOUD_SECRET_KEY")
BUCKET_NAME      = ReadEnvVar("BUCKET_NAME")

# creating an client instance
s3 = boto3.client(
    "s3",
    endpoint_url=CLOUD_ENDPOINT,
    aws_access_key_id=CLOUD_ACCESS_KEY,
    aws_secret_access_key=CLOUD_SECRET_KEY  
)

db = Database()


async def ProcessImages(event, client, data, isAlbum):
    # list of task for proccessing in parallel 
    tasks = []
    
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

            paths.append(file_path.replace("\\\\", "/"))

            # appending tasks to taskts list 
            tasks.append(UploadToCloud(file_path, filename))

    # if it's only one image
    else:
        photo = event.message.photo

        # generating file name based on photo id
        filename = f"{event.chat.id}-{event.message.id}.jpg"
        # downloading photo into the machine
        file_path = await client.download_media(photo, f"./media/{filename}")
        paths.append(file_path.replace("\\\\", "/"))        

        # adding task to tasks list
        tasks.append(UploadToCloud(file_path, filename))
    
    # gathering returned values from the tasks list
    image_urls = await asyncio.gather(*tasks)

    # sending message to channel
    data["images"] = paths
    message_ids = await SendToChannel(client, data)
    # adding post ids in database so it can be accessable 
    data["channel_posts_id"] = message_ids

    # removing proccessed images
    for path in paths:
        os.remove(path)

    return image_urls


# this function uploads to cloud using boto3
async def UploadToCloud(file_path, object_name):
    # getting event loop
    loop = asyncio.get_event_loop()


    try:
        # runs an executer
        await loop.run_in_executor(None, s3.upload_file, file_path, BUCKET_NAME, object_name)
        
        # returning url of image so it can be accessed in website
        return f"https://{BUCKET_NAME}.s3.ir-thr-at1.arvanstorage.ir/{object_name}"
    
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return None
    

async def DeleteImage(filename):
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
        
    except Exception as e:
        logging.error(f"Error deleting file: {e}")