import logging
import os
from dotenv import load_dotenv



class ChannelsCode:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChannelsCode, cls).__new__(cls)
            cls._instance.channels = {}

        return cls._instance

    def add_codes(self, key, value):
        self.channels[key] = value 


    def get_codes(self):
        return self.channels



load_dotenv()

def ReadEnvVar(name: str):
    value = os.getenv(name)

    return value

ROOT_DIR = ReadEnvVar("ROOT_DIR")


CHANNEL_USERNAME = ReadEnvVar("CHANNEL_USERNAME")


# reading username of channels in file
def ReadChannels(filepath: str):
    
    codes = ChannelsCode()
    
    try:
        file = open(filepath, "r")
        channels = file.read().splitlines()
        for idx in range(len(channels)):
            values = channels[idx].split()

            if len(values) < 2:
                continue

            codes.add_codes(values[0], values[1])

        return channels
    except Exception as e:
        logging.error(f"Error reading {filepath}: {e}")