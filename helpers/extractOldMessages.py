from . import tools
from telethon.tl.functions.channels import JoinChannelRequest
from . import messageParser
from .utils import ReadChannels
import asyncio
from db.main import Database
import asyncio
from db.main import Database
import random
from .tools import Create_Data
import logging


db = Database()

async def JoinChannels(client, filepath: str):
    
    channels = ReadChannels(filepath)


    for channel in channels:
        channel = channel.split()[0]
        await asyncio.sleep(random.uniform(2, 8))
        
        entity = await client.get_entity(channel)
        await client(JoinChannelRequest(channel))
        
        try:
            # iterating over channel's messages
            async for message in client.iter_messages(entity, limit=200):
                # get a channel 
                await asyncio.sleep(random.uniform(2,5))
                if message.grouped_id:
                    
                    if message.text:
                        if "روتین" in message.text or "فروخته"in message.text or "فروش"  in message.text:
                            continue
                        # finding matches in text
                        matches = messageParser.ParseMessage(message.text)
                        
                        media = await get_media_posts_in_group(client, entity.id, message)
                        message.messages = media
                        if len(media) > 0:
                            await Create_Data(client, matches, db, message, False, True, True)

                else:
                    if message.text and message.photo:
                        if "روتین" in message.text or "فروخته"in message.text:
                            continue
                        # geetting  matched from the text
                        matches = messageParser.ParseMessage(message.text)

                        await tools.Create_Data(client, matches, db , message, False, False, True)
        except Exception as e:
            logging.warning(f"Rate limited! Sleeping for {e.seconds} seconds...")
            await asyncio.sleep(e.seconds)


async def get_media_posts_in_group(client, chat, original_post, max_amp=5):
    if original_post.grouped_id is None:
        return [original_post] if original_post.media is not None else []

    search_ids = [i for i in range(original_post.id - max_amp, original_post.id + max_amp + 1)]
    posts = await client.get_messages(chat, ids=search_ids)
    media = []
    for post in posts:
        if post is not None and post.grouped_id == original_post.grouped_id and post.media is not None:
            media.append(post)
    return media

