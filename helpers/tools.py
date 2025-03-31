import json
import re
from telethon.types import Message
from .utils import ChannelsCode
from .media import ProcessImages


# a function to remove phone numbers, links and username also it deletes some unecessary characters
def CleanText(text):
    text = re.sub(r"\bیک\b" , "1", text)
    # removing narrow space
    text = text.replace("\u200c", " ")
    # adding space between word and numbers
    text = re.sub(r'([^\d۰-۹])([\d۰-۹])', r'\1 \2', text)
    text = re.sub(r'([\d۰-۹])([^\d۰-۹])', r'\1 \2', text)  
    text = "\n".join(" ".join(line.split()) for line in text.split("\n"))
    # removing emojies
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  
        u"\U0001F300-\U0001F5FF"  
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
                           "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text) 
    
    text = re.sub(r"\b[a-zA-Z]\b", "", text)
    text = text[:text.index("قیمت")] if "قیمت" in text else text
    text = "\n".join(" ".join(line.split()) for line in text.split("\n") if "تماس" not in line)
    text = "\n".join(" ".join(line.split()) for line in text.split("\n") if "فروش" not in line)
    text = "\n".join(" ".join(line.split()) for line in text.split("\n") if "سایز" not in line and "*" not in line)
    text = "\n".join(" ".join(line.split()) for line in text.split("\n") if "×" not in line)
    text = "\n".join(" ".join(line.split()) for line in text.split("\n") if not line.isdigit())
    # text = "\n".join(text.split())
    text = text.replace('درجه ۱', "درجه یک")
    text = text.replace('درجه 1', "درجه یک")
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'(\+?۹۸|۰|\+?98|0)[۰-۹0-9]{10}', '', text)  # Matches +98 or 0 followed by 9 and then 9 digits
    
    # Remove links (URLs starting with http://, https:// or www.)
    text = re.sub(r'http[s]?://\S+|www\.\S+', '', text)
    
    # Remove usernames (words starting with @)
    text = re.sub(r'@\w+', '', text)

    characters = ["+",".", "/", "\\", ",", "،", "$", "#", "@", "*", "!", "٫", "(", ")"]

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
        text = text.replace(EnglishToPersianNumbers(value), "")
        
    
    if "شانه" in text or re.search(r"\bش\b|[\d\u06F0-\u06F9]+\s*ش|ش\s*[\d\u06F0-\u06F9]+", text) is not None or text in ["1500", "1000", "700", "1200", "۱۲۰۰", "۱۰۰۰", "۷۰۰", "۱۵۰۰"]:
        comb = EnglishToPersianNumbers(str(data["comb"]))
        if "شانه" in text:
            text = text.replace("شانه", "")
        else:
            text = re.sub(r"\bش\b|[\d\u06F0-\u06F9]+\s*ش|ش\s*[\d\u06F0-\u06F9]+", "", text)

        text = text.replace(comb, "")
        # for english numbers in text
        text = text.replace(str(data['comb']), "")

    text = text.replace("متری", " ")
    text = text.replace("متر", " ")


    # checks if the نخته is in the match and if it is it will be considered as quantity in Sizes class
    if "تخته" in text or "تخت" in text or re.search(r"\bت\b|[\d\u06F0-\u06F9]ت\s*[\d\u06F0-\u06F9]+", text) is not None:
        if "تخته" in text:
            text = text.replace("تخته", " ")
        else:
            text = re.sub(r"\bت\b|[\d\u06F0-\u06F9]|ت\s*[\d\u06F0-\u06F9]+", "", text)


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
    text = text.replace(data["title"], "")

    return " ".join(text.split())


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
            if values[0] not in [12,6,9]:
                return
            self._instance.listOfSizes.append(values)
            self._instance.listOfData = [None, None] 
    
    # getting the sizes and quantities store
    def get_sizes(self):
        
        sizes = self._instance.listOfSizes
        seen = {}
        unique_sizes = []
    
        for size in sizes:
            key = size[0]  # Use the first element as the key
            if key not in seen:
                seen[key] = True
                unique_sizes.append(size)  # Keep only the first occurrence
    
        self._instance.listOfSizes = unique_sizes  # Update original list
        return unique_sizes

    # using this to prevent from storing previous products info
    def destroy(self):
        self._instance.listOfSizes = []




# this simply returns a python dict containing products information that is represented for database fields 
async def Create_Data(client, extractedWords: list[str], db, event, edited=False, isAlbum=None, isOldMessage=False):
 
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

    channel_codes = ChannelsCode().get_codes()

    code = channel_codes[event.chat.username]

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
        elif "تخته" in word or "تخت" in word or re.search(r"(?<!\S)[\d\u06F0-\u06F9]*ت|[\d\u06F0-\u06F9]ت(?!\S)", word) is not None:
            if "تخته" in word:
                quantity = word.replace("تخته", "")
            else:
                quantity = word.replace("ت", "")

            size.add_data(int(quantity), 1)
        
        # checks if شانه is in the match and if it is it will clean it and consider it as comb
        elif "شانه" in word or re.search(r"(?<!\S)[\d\u06F0-\u06F9]*ش|[\d\u06F0-\u06F9]ش(?!\S)", word) is not None or word in ["1500", "1000", "700", "1200", "۱۲۰۰", "۱۰۰۰", "۷۰۰", "۱۵۰۰"]:
            if data["comb"] != 0:
                continue
            if "شانه" in word:
                comb = word.replace("شانه", "")
            else:
                comb = word.replace("ش", "")

            data["comb"] = int(comb)

        # detecting the actual size
        elif word in ["6", "9", "12", "۱۲", "۹", "۶"] or "متر" in word:
            length = int(word.replace("متر", ""))
            size.add_data(length, 0)


    data["sizes"] = size.get_sizes()

    data["title"] = ExtractWithoutDuplicateInfo(extractedWords[-1], data)
    data["details"] = ExtractWithoutDuplicateInfo(event.text, data).replace("فرش", "")
    
    if len(data["details"]) < 2 or len(data['details'].split()) < 2:
        data['details'] = ""

    if not data["title"]:
        data["title"] = f"فرش {data['comb']} شانه"

    if not data["comb"] or data["comb"] == 0 or len(data['sizes']) == 0 or data["comb"] not in [1200,700,1000,1500]:
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


        await db.update_products(channel_id, message_id ,*data.values())