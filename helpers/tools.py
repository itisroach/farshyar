from dotenv import load_dotenv
import os

load_dotenv()


def ReadEnvVar(name: str):
    value = os.getenv(name)

    return value

