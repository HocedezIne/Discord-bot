import logging
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

class Bot:
    def __init__(self, token, prefix="!"):
        self.token = token

        self.bot = commands.Bot(command_prefix=prefix, allowed_mentions=discord.AllowedMentions(replied_user=False))
        self.bot.load_extension("Extensions.alarmclock")

        self.start()
    
    async def on_ready(self):
        logging.info(f"{self.bot.user.name} has connected to Discord")

    def start(self):
        self.bot.run(self.token)


logging.basicConfig(level=logging.DEBUG)

load_dotenv(dotenv_path=f'{os.path.dirname(__file__)}/data/.env')
TOKEN = os.getenv('DISCORD_TOKEN')

if (__name__ == "__main__"):
    try:
        bot = Bot(TOKEN, "!")
    except KeyboardInterrupt as ex:
        exit()
    # except Exception as ex:
    #     logging.critical(ex)
    #     exit()

    finally:
        print("Bot shut down")