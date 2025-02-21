from dotenv import load_dotenv
import os

load_dotenv()


def ReadEnvVar(name: str):
    value = os.getenv(name)

    return value


def Create_Data(extractedWords: list[str]):

    data = {
        "title": "",
        "details": "",
        "quantity": 0
    }

    for word in extractedWords:
        if "فرش" in word:
            data["title"] = word
        
        
        elif "تخته" in word:
            data["quantity"] = int(word.replace("تخته", ""))

        else:
            data["details"] += word


    print(data)