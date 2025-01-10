import discord
from discord.ext import commands, tasks

# Token and prefix in a separate config.py file, untracked for token purposes
from config import PREFIX, BOT_TOKEN, SHUTDOWN_IDS
from assets import IMAGES
from random import choice
import asyncio
import aiohttp
import os

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


@bot.command()
async def test(ctx):
    await ctx.send(f"Hey {ctx.author.mention}, your test worked!")


@bot.command(name="embed")
async def test_embed(
    ctx, title: str = "Title of embed", desc: str = "Description of embed"
):
    embed_msg = discord.Embed(
        title=title, description=desc, color=discord.Colour(0xFFD1DC)
    )
    embed_msg.set_thumbnail(url=IMAGES["LOTUS"])
    embed_msg.add_field(name="Test field name", value="Test field value", inline=False)
    embed_msg.add_field(name="Server picture", value=None, inline=False)
    embed_msg.set_image(url=ctx.guild.icon)
    embed_msg.set_footer(
        text="Finally, a footer. Here's your pfp :3", icon_url=ctx.author.avatar
    )
    await ctx.send(embed=embed_msg)


@bot.command()
async def ping(ctx):
    ping_embed = discord.Embed(title="Ping", description="Latency in ms")
    ping_embed.add_field(
        name=f"{bot.user.name}'s latency", value=f"{round(bot.latency * 1000)}ms"
    )
    ping_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)
    await ctx.send(embed=ping_embed)


@bot.command()
async def shutdown(ctx):
    if ctx.author.id not in SHUTDOWN_IDS:
        await ctx.send("Sorry, only the bot creator can use this command.")
    else:
        await ctx.send("Shutting down...")
        print("Closing!")
        await bot.close()


"""
@bot.command(name="bot_help")
async def bot_help(ctx):
    embed = discord.Embed(
        title="Cephalon Nahla Commands",
        description=f"Use {PREFIX} before the commands.",
        color=discord.Color(0xFFD1DC),
    )
    embed.add_field(name="Note", value="Slash commands to be added soon", inline=False)
    embed.add_field(name="test", value="Prints a test message", inline=False)
    embed.add_field(name="embed", value="Creates a test embed", inline=False)
    embed.add_field(name="ping", value="Shows your ping to the bot", inline=False)
    embed.add_field(
        name="shutdown",
        value="Shuts down the bot if your ID is in the whitelist",
        inline=False,
    )
    await ctx.send(embed=embed)
"""


async def main():
    async with bot:
        await load()
        await bot.start(BOT_TOKEN)


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


asyncio.run(main())
