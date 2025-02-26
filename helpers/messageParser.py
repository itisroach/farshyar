import re
from . import tools

# finding matches of important information that we need
def ParseMessage(message: str):

    message = tools.CleanText(message)
    print(message)

    pattern = r"(\d{4}\s?شانه|\d{3}\s?شانه|\d+\s?ش|\d{1,2}\s?ت|[\d]+(?:\s?متر|متری|متراژ)?|کد\s?\d+|\d+)"
    title_pattern = r"^(.*)"
    matches = re.findall(pattern, message)
    
    foundTitle = re.findall(title_pattern, message)


    matches.append(foundTitle[0])

    print("matches",matches)
    

    return matches
    



