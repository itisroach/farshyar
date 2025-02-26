import boto3 
import asyncio
import os
from db.main import Database
from .tools import ReadEnvVar, Create_Data

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


async def ProcessImages(event, client, extractedWords, isAlbum):
    # list of task for proccessing in parallel 
    tasks = []
    
    # check if it is multiple images 
    if isAlbum:
        # iterating through all images
        for image in event.messages:
            # genearting unique file name based on ids
            filename = f"{image.grouped_id}-{image.id}.jpg"
            # uploading file locally on machine
            file_path = await client.download_media(image, f"./media/{filename}")

            # appending tasks to taskts list 
            tasks.append(UploadToCloud(file_path, filename))

    # if it's only one image
    else:
        photo = event.message.photo

        # generating file name based on photo id
        filename = f"{photo.id}.jpg"
        # downloading photo into the machine
        file_path = await client.download_media(photo, f"./media/{filename}")

        # adding task to tasks list
        tasks.append(UploadToCloud(file_path, filename))
    
    # gathering returned values from the tasks list
    image_urls = await asyncio.gather(*tasks)

    # creating data and inserting the to database
    await Create_Data(extractedWords, image_urls, db, event)


# this function uploads to cloud using boto3
async def UploadToCloud(file_path, object_name):
    # getting event loop
    loop = asyncio.get_event_loop()


    try:
        # runs an executer
        await loop.run_in_executor(None, s3.upload_file, file_path, BUCKET_NAME, object_name)
        # removing the uploaded file from the machine
        os.remove(file_path)
        # returning url of image so it can be accessed in website
        return f"https://{BUCKET_NAME}.s3.ir-thr-at1.arvanstorage.ir/{object_name}"
    
    except Exception as e:
        print(e)
        return None