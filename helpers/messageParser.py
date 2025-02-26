import re
from . import tools

# finding matches of important information that we need
def ParseMessage(message: str):

    message = CleanText(message)
    print(message)

    pattern = r"(\d{4}\s?شانه|\d{3}\s?شانه|\d+\s?ش|\d{1,2}\s?ت|[\d]+(?:\s?متر|متری|متراژ)?|کد\s?\d+|\d+)"
    title_pattern = r"^(.*)"
    matches = re.findall(pattern, message)
    
    foundTitle = re.findall(title_pattern, message)


    matches.append(foundTitle[0])

    print("matches",matches)
    

    return matches
    

# a function to remove phone numbers, links and username also it deletes some unecessary characters
def CleanText(text):
    text = re.sub(r'(\+?۹۸|۰|\+?98|0)[۰-۹0-9]{10}', '', text)  # Matches +98 or 0 followed by 9 and then 9 digits
    
    # Remove links (URLs starting with http://, https:// or www.)
    text = re.sub(r'http[s]?://\S+|www\.\S+', '', text)
    
    # Remove usernames (words starting with @)
    text = re.sub(r'@\w+', '', text)

    characters = [".", "/", "\\", ",", "،", "$", "#", "@", "*", "!"]

    for c in characters:
        text = text.replace(c, "")

    return text.strip()

