import discord
from discord.ext import commands, tasks

# Token and prefix in a separate config.py file, untracked for token purposes
from config import PREFIX, BOT_TOKEN
from random import choice
import asyncio
import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

possible_statuses = [
    "Stalking the Stalker...",
    "Rerolling riven mods",
    "/unstuck simulator",
    "Hey, Kiddo.",
    "Cleaning up after your Kubrow",
    "Being Ordis's friend <3",
    "Farming Simulator 3025",
    "Having the Party of Your Lifetime",
    "ERR;[-=,TECHROT CORRUPTION DETECTED",
    "I am sad to report that all my good jokes Argon.",
    "where baro?",
    "how is baro?",
    "Off-Lyne :(",
]


@tasks.loop(seconds=5)
async def change_bot_status():
    status = str(choice(possible_statuses))
    if status == "Hey, Kiddo.":
        change_bot_status.change_interval(seconds=60)
    else:
        change_bot_status.change_interval(seconds=600)
    await bot.change_presence(activity=discord.CustomActivity(status))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    change_bot_status.start()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content
    tokens = content.split(" ")
    if tokens[0] == PREFIX + "test":
        await message.channel.send("Test complete.")


async def main():
    await bot.start(BOT_TOKEN)


asyncio.run(main())
