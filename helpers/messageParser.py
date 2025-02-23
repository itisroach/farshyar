import re
from . import tools

def ParseMessage(message: str):
    pattern = r"(\d{4}\s?شانه|\d{3}\s?شانه|\d+\s?ش|\d{1,2}\s?ت|[\d]+(?:\s?متر|متری|متراژ)?|کد\s?\d+|\d+)"
    title_pattern = r"^(.*)"
    matches = re.findall(pattern, message)
    
    foundTitle = re.findall(title_pattern, message)


    print("matches",matches)

    matches.append(foundTitle[0])

    
    data = tools.Create_Data(matches)

    return data
    
