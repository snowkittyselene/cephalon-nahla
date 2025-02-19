import discord
from discord.ext import commands, tasks

# Token and prefix in a separate config.py file, untracked for token purposes
from config import PREFIX, BOT_TOKEN, SHUTDOWN_IDS, DEV_GUILD_ID
from random import choice
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
dev_guild = None

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
    dev_guild = discord.utils.get(bot.guilds, id=DEV_GUILD_ID)
    if dev_guild is None:
        print("Couldn't find dev guild. Shutting down.")
        return
    print(f"Logged in as {bot.user}!")
    change_bot_status.start()


@bot.tree.command(
    name="resync_commands",
    description="Re-sync the commands. Usable only by authorised people.",
    guild=dev_guild,
)
async def resync_commands(ctx: discord.Interaction):
    if ctx.user.id not in SHUTDOWN_IDS:
        await ctx.response.send_message(
            f"Only authorised users can use this command.", ephemeral=True
        )
        return
    try:
        synced_commands = await bot.tree.sync()
        await ctx.response.send_message(
            f"Synced {len(synced_commands)} commands", ephemeral=True
        )
    except Exception as e:
        print(f"Error while syncing commands: {e}")


@bot.command(
    name="resync_commands",
    description="Re-sync the commands. Usable only by authorised people.",
)
async def resync_commands(ctx):
    if ctx.author.id not in SHUTDOWN_IDS:
        await ctx.send(f"Only authorised users can use this command.", ephemeral=True)
        return
    try:
        synced_commands = await bot.tree.sync()
        await ctx.send(f"Synced {len(synced_commands)} commands", ephemeral=True)
    except Exception as e:
        print(f"Error while syncing commands: {e}")


@bot.tree.command(name="ping", description="Shows your ping")
async def ping(interaction: discord.Interaction):
    ping_embed = discord.Embed(title="Ping", description="Latency in ms")
    ping_embed.add_field(
        name=f"{bot.user.name}'s latency", value=f"{round(bot.latency * 1000)}ms"
    )
    ping_embed.set_author(
        name=interaction.user.display_name, icon_url=interaction.user.avatar
    )
    await interaction.response.send_message(embed=ping_embed, ephemeral=True)


@bot.tree.command(
    name="shutdown",
    description="Shuts down the bot. Usable only by authorised users.",
    guild=dev_guild,
)
async def shutdown(ctx: discord.Interaction):
    if ctx.user.id not in SHUTDOWN_IDS:
        await ctx.response.send_message(
            "Sorry, only authorised users can use this command.", ephemeral=True
        )
    else:
        await ctx.response.send_message("Shutting down...")
        print("Closing!")
        await bot.close()


@bot.tree.command(
    name="reload_cog",
    description="Reloads a specified cog. Usable only by authorised users",
    guild=dev_guild,
)
async def reload_cog(ctx: discord.Interaction, cog_name: str):
    if ctx.user.id not in SHUTDOWN_IDS:
        await ctx.response.send_message(
            "Sorry, only authorised users can use this.", ephemeral=True
        )
    else:
        await ctx.response.send_message(f"Restarting {cog_name}...", ephemeral=True)
        await bot.reload_extension(f"cogs.{cog_name}")


async def main():
    async with bot:
        await load()
        await bot.start(BOT_TOKEN)


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


asyncio.run(main())
