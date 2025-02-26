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

# a function to extract title and delete unecessary words from it
def ExtractTitle(title, data):
    
    # clean up the title
    for value in data.values():

        title = title.replace(str(value), "")
        
    
    if "شانه" in title or re.search(r"(?<!\S)[\d\u06F0-\u06F9]*ش|[\d\u06F0-\u06F9]ش(?!\S)", title) is not None or title in ["1500", "1000", "700", "1200", "۱۲۰۰", "۱۰۰۰", "۷۰۰", "۱۵۰۰"]:
        comb = EnglishToPersianNumbers(data["comb"])
        if "شانه" in title:
            title = title.replace("شانه", "")
        else:
            title = title.replace("ش", "")

        title = title.replace(comb, "")
        # for english numbers in text
        title = title.replace(str(data["comb"]), "")

    if "۱۰۰٪" not in title and "اکریلیک" not in title and "اکرلیک" not in title:
        title += " ۱۰۰٪ اکریلیک " 

    return title.strip().replace("  ", " ")

# a function to extrac details about products from the whole message
def ExtractDescription(text, data):
    # clean up the description
    for value in data.values():

        text = text.replace(str(value), "")
        
    
    if "شانه" in text or re.search(r"(?<!\S)[\d\u06F0-\u06F9]*ش|[\d\u06F0-\u06F9]ش(?!\S)", text) is not None or text in ["1500", "1000", "700", "1200", "۱۲۰۰", "۱۰۰۰", "۷۰۰", "۱۵۰۰"]:
        comb = EnglishToPersianNumbers(data["comb"])
        if "شانه" in text:
            text = text.replace("شانه", "")
        else:
            text = text.replace("ش", "")

        text = text.replace(comb, "")
        # for english numbers in text
        text = text.replace(str(data["comb"]), "")

    text = text.replace("متری", "")
    text = text.replace("متر", "")

    for size in data["sizes"]:
        text = text.replace(EnglishToPersianNumbers(size[0]), "")
        # for english numbers in text
        text = text.replace(str(size[0]), "")

        text = text.replace(EnglishToPersianNumbers(size[1]), "")
        # for english numbers in text
        text = text.replace(str(size[1]), "")

    # checks if the نخته is in the match and if it is it will be considered as quantity in Sizes class
    if "تخته" in text or re.search(r"(?<!\S)[\d\u06F0-\u06F9]*ت|[\d\u06F0-\u06F9]ت(?!\S)", text) is not None:
        if "تخته" in text:
            text = text.replace("تخته", "")
        else:
            text = text.replace("ت", "")



    text = text.strip().replace("  ", " ")
    return text.replace("\n", " ")

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
async def Create_Data(extractedWords: list[str], images: list[str], db, event, edited=False):
    # getting information about chat
    chat_info = await event.get_chat()

    # getting the message id
    message_id = str(event.original_update.message.id)
    channel_id = str(chat_info.id)


    data = {
        "title": "",
        "details": "",
        "sizes": [],
        "comb": 0,
        "post_link": GeneratePostLink(chat_info.id, message_id),
        "post_id": message_id,
        "channel_id": chat_info.id,
        "images": images
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

    data["title"] = ExtractTitle(extractedWords[-1], data)
    data["details"] = ExtractDescription(event.text, data).replace("فرش", "")

    if (not data["comb"] and not data["title"]) or len(data['sizes']) == 0:
        return

    # convert the Size class output to json so it can be stored in database
    data["sizes"] = json.dumps(data["sizes"])

    # destory the class intance for further use to bed intialized
    size.destroy()


    if edited == False:
        # inserting product to database
        await db.add_products(*data.values())
    else:
        data = {
            "title": data["title"],
            "details": data["details"],
            "sizes": data["sizes"],
            "comb": data["comb"]
        }

        if (not data["comb"] and not data["title"]) or len(data['sizes']) == 0:
            return


        await db.update_products(channel_id,message_id ,*data.values())
    
