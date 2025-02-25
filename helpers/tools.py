from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

def ReadEnvVar(name: str):
    value = os.getenv(name)

    return value

# generate a link of telegram message to be accessed 
def GeneratePostLink(channel_username, message_id):
    link = f"https://t.me/c/{channel_username}/{message_id}"

    return link

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
async def Create_Data(extractedWords: list[str], images: list[str], db, event):

    # getting information about chat
    chat_info = await event.get_chat()

    # getting the message id
    message_id = event.original_update.message.id

    data = {
        "title": extractedWords[-1],
        "details": "",
        "sizes": [],
        "comb": 0,
        "post_link": GeneratePostLink(chat_info.id, message_id),
        "post_id": str(message_id),
        "channel_id": str(chat_info.id),
        "images": images
    }
    size = Sizes()

    for idx, word in enumerate(extractedWords):
        
        # checking if the word that it reaches is not the title and if it is not the title it removes every other match in the title 
        if idx != len(extractedWords)-1:
            extractedWords[-1] = extractedWords[-1].replace(word, "") 
            data["title"] = extractedWords[-1].strip().replace(" ", " ")

        # if theres code in title it will remove it
        if "کد" in word:    
            data["title"] = re.sub(r"کد\s+\S+", "", extractedWords[-1]).strip()
            data["title"] = data["title"].replace("  " , " ")

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


    data["title"] = f"{data["title"]} ۱۰۰٪ اکریلیک"

    # convert the Size class output to json so it can be stored in database
    data["sizes"] = (json.dumps(size.get_sizes()))

    # destory the class intance for further use to bed intialized
    size.destroy()

    
    # inserting product to database
    await db.add_products(*data.values())

    
