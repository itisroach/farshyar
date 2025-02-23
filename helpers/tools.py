from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

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

def ReadEnvVar(name: str):
    value = os.getenv(name)

    return value


# this simply returns a python dict containing products information that is represented for database fields 
def Create_Data(extractedWords: list[str]):

    data = {
        "title": extractedWords[-1],
        "details": "",
        "sizes": [],
        "comb": 0,
        "post_link": "",
        "post_id": ""
    }
    size = Sizes()
    for word in extractedWords:
        data["title"] = extractedWords[-1]
        # if theres code in title it will remove it
        if "کد" in word:    
            data["title"] = re.sub(r"کد\s+\S+", "", extractedWords[-1]).strip()
            data["title"] = data["title"].replace("  " , "")

        elif "تخته" in word or re.match(r"(?<!\S)\d*ت|\dت(?!\S)", word):
            quantity = word.replace("تخته", "")
            quantity = re.sub(r'(\d)[\u0600-\u06FF]', r'\1', word)

            size.add_data(int(quantity), 1)
        
        elif "شانه" in word or re.match(r"(?<!\S)\d*ش|\dش(?!\S)"):
            if "شانه" in word:
                comb = word.replace("شانه", "")
            else:
                comb = word.replace("ش", "")

            data["comb"] = int(comb)

        
        elif word in ["4", "6", "9", "12", "۱۲", "۴", "۹", "۶"] or "متر" in word:
            word = word.replace("متر", "")
            length = int(word)
            size.add_data(length, 0)


    data["sizes"] = (json.dumps(size.get_sizes()))

    size.destroy()

    return data
