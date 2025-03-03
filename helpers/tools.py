import asyncio
import os
import json
import re
from telethon.types import Message
from .utils import ChannelMessage
from .media import ProcessImages


# a function to remove phone numbers, links and username also it deletes some unecessary characters
def CleanText(text):
    text = text.replace('درجه ۱', "درجه یک")
    text = text.replace('درجه 1', "درجه یک")
    text = re.sub(r'(\+?۹۸|۰|\+?98|0)[۰-۹0-9]{10}', '', text)  # Matches +98 or 0 followed by 9 and then 9 digits
    
    # Remove links (URLs starting with http://, https:// or www.)
    text = re.sub(r'http[s]?://\S+|www\.\S+', '', text)
    
    # Remove usernames (words starting with @)
    text = re.sub(r'@\w+', '', text)

    characters = [".", "/", "\\", ",", "،", "$", "#", "@", "*", "!", "٫"]

    for c in characters:
        text = text.replace(c, "")

    return text.strip()

# generate a link of telegram message to be accessed 
def GeneratePostLink(channel_username, message_id):
    link = f"https://t.me/c/{channel_username}/{message_id}"

    return link

# a function to extrac details about products from the whole message
def ExtractWithoutDuplicateInfo(text, data):
    text = CleanText(text)

    # clean up the description
    for value in data.values():

        text = text.replace(str(value), "")
        
    
    if "شانه" in text or re.search(r"\bش\b|[\d\u06F0-\u06F9]+\s*ش|ش\s*[\d\u06F0-\u06F9]+", text) is not None or text in ["1500", "1000", "700", "1200", "۱۲۰۰", "۱۰۰۰", "۷۰۰", "۱۵۰۰"]:
        comb = EnglishToPersianNumbers(data["comb"])
        if "شانه" in text:
            text = text.replace("شانه", "")
        else:
            text = re.sub(r"\bش\b|[\d\u06F0-\u06F9]+\s*ش|ش\s*[\d\u06F0-\u06F9]+", "", text)

        text = text.replace(comb, "")
        # for english numbers in text
        text = text.replace(str(data["comb"]), "")

    text = text.replace("متری", "")
    text = text.replace("متر", "")


    # checks if the نخته is in the match and if it is it will be considered as quantity in Sizes class
    if "تخته" in text or re.search(r"\bت\b|[\d\u06F0-\u06F9]+\s*ت|ت\s*[\d\u06F0-\u06F9]+", text) is not None:
        if "تخته" in text:
            text = text.replace("تخته", "")
        else:
            text = re.sub(r"\bت\b|[\d\u06F0-\u06F9]+\s*ت|ت\s*[\d\u06F0-\u06F9]+", "", text)


    for size in data["sizes"]:
        pattern = fr"\b{size[0]}\b|\b{size[1]}\b|ت\s*(?:{size[0]})"
        text = re.sub(pattern, "", text).strip()
        pattern = rf"(?<!\S){EnglishToPersianNumbers(size[0])}(?!\S)|(?<!\S){EnglishToPersianNumbers(size[1])}(?!\S)|ت\s*(?:{EnglishToPersianNumbers(size[0])})"
        text = re.sub(pattern, "" , text).strip()

    text = text.replace("فرش", "")
    text = text.replace("موجود است", "")
    text = text.replace("موجود میباشد", "")
    text = text.replace("موجود می باشد", "")
    text = text.strip().replace("  ", "\n")

    return text


# a function to simply convert English digits to Persian digits
def EnglishToPersianNumbers(number):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"

    dictionary = str.maketrans(english_digits, persian_digits)
    
    return str(number).translate(dictionary)

# a data type that can generate a list of tuples that can store tuples like this (size, quantity) this is for knowing how many stocks we have in each size
class Sizes():
    _instance = None
    
    # creating only one instance 
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Sizes, cls).__new__(cls)
            cls._instance.listOfData = [None, None]
            cls._instance.listOfSizes = []
            
        return cls._instance
    

    def add_data(self, data, index):
        # adding data to desired index
        self._instance.listOfData[index] = data

        # if both indexes of tuple like is filled it will be store them as tuple in a list
        if len(self._instance.listOfData) == 2 and (self._instance.listOfData[0] is not None and self._instance.listOfData[1] is not None):
            values = tuple(self._instance.listOfData)
            self._instance.listOfSizes.append(values)
            self._instance.listOfData = [None, None] 
    
    # getting the sizes and quantities store
    def get_sizes(self):
        return self._instance.listOfSizes

    # using this to prevent from storing previous products info
    def destroy(self):
        self._instance.listOfSizes = []




# this simply returns a python dict containing products information that is represented for database fields 
async def Create_Data(client, extractedWords: list[str], db, event, edited=False, isAlbum=None):
    
    if event is not Message:
        # getting information about chat
        chat_info = await event.get_chat()
        channel_id = str(chat_info.id)

    else:
        channel_id = str(event.chat.id)

    # getting the message id
    message_id = None 
    try:
        message_id = str(event.original_update.message.id)
    except Exception as e:
        message_id = str(event.id)

    code = str(event.chat.id)[-4:]

    data = {
        "code": code,
        "title": "",
        "details": "",
        "sizes": [],
        "comb": 0,
        "post_link": GeneratePostLink(channel_id, message_id),
        "post_id": message_id,
        "channel_id": channel_id
    }
    size = Sizes()

    for idx, word in enumerate(extractedWords):
        
        # it does not read and apply below code to the title
        if idx == len(extractedWords)-1:
            continue

        # checks if the نخته is in the match and if it is it will be considered as quantity in Sizes class
        elif "تخته" in word or re.search(r"(?<!\S)[\d\u06F0-\u06F9]*ت|[\d\u06F0-\u06F9]ت(?!\S)", word) is not None:
            if "تخته" in word:
                quantity = word.replace("تخته", "")
            else:
                quantity = word.replace("ت", "")

            size.add_data(int(quantity), 1)
        
        # checks if شانه is in the match and if it is it will clean it and consider it as comb
        elif "شانه" in word or re.search(r"(?<!\S)[\d\u06F0-\u06F9]*ش|[\d\u06F0-\u06F9]ش(?!\S)", word) is not None or word in ["1500", "1000", "700", "1200", "۱۲۰۰", "۱۰۰۰", "۷۰۰", "۱۵۰۰"]:
            if "شانه" in word:
                comb = word.replace("شانه", "")
            else:
                comb = word.replace("ش", "")

            data["comb"] = int(comb)

        # detecting the actual size
        elif word in ["4", "6", "9", "12", "۱۲", "۴", "۹", "۶"] or "متر" in word:
            length = int(word.replace("متر", ""))
            size.add_data(length, 0)


    data["sizes"] = size.get_sizes()

    data["title"] = ExtractWithoutDuplicateInfo(extractedWords[-1], data)
    data["details"] = ExtractWithoutDuplicateInfo(event.text, data).replace("فرش", "")

    if not data["title"]:
        data["title"] = f"فرش {data["comb"]} شانه"

    if not data["comb"] or data["comb"] == 0 or len(data['sizes']) == 0:
        return

    # convert the Size class output to json so it can be stored in database
    data["sizes"] = json.dumps(data["sizes"])

    # destory the class intance for further use to bed intialized
    size.destroy()


    if edited == False:
        urls = None
        # inserting product to database
        if isAlbum is not None:

            images = await ProcessImages(event, client, data, isAlbum)
            urls = images   
        else:
            channel_message = ChannelMessage(client, data)
            data["channel_posts_id"] = await channel_message.SendToChannel(images=None)
    
        inserted_id = await db.add_products(*data.values())
        if urls is not None:
            await db.add_images(inserted_id, urls)
    else:
    
        data = {
            "title": data["title"],
            "details": data["details"],
            "sizes": data["sizes"],
            "comb": data["comb"]
        }
    
        if (not data["comb"] and not data["title"]) or len(data['sizes']) == 0:
            return


        channel_posts_id = await db.update_products(channel_id, message_id ,*data.values())
        # updating message in the main chanell
        message_id = json.loads(channel_posts_id[0]["channel_posts_id"])
        message_id = message_id[0]
        channel_message = ChannelMessage(client, data)
        await channel_message.EditChannelMessage(message_id)    