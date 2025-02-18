import discord
from discord.ext import commands, tasks

# Token and prefix in a separate config.py file, untracked for token purposes
from config import PREFIX, BOT_TOKEN, SHUTDOWN_IDS
from assets import IMAGES
from random import choice
import asyncio
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


@bot.tree.command(name="test", description="Pings the user")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hey {interaction.user.mention}, your test worked!"
    )


@bot.tree.command(name="embed_test", description="Prints a test embed")
async def test_embed(
    interaction: discord.Interaction,
    title: str = "Title of embed",
    desc: str = "Description of embed",
):
    embed_msg = discord.Embed(
        title=title, description=desc, color=discord.Colour(0xFFD1DC)
    )
    embed_msg.set_thumbnail(url=IMAGES["LOTUS"])
    embed_msg.add_field(name="Test field name", value="Test field value", inline=False)
    embed_msg.add_field(name="Server picture", value=None, inline=False)
    embed_msg.set_image(url=interaction.guild.icon)
    embed_msg.set_footer(
        text="Finally, a footer. Here's your pfp :3", icon_url=interaction.user.avatar
    )
    await interaction.response.send_message(embed=embed_msg, ephemeral=True)


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


@bot.command(
    name="shutdown", description="Shuts down the bot. Usable only by authorised users."
)
async def shutdown(ctx):
    if ctx.author.id not in SHUTDOWN_IDS:
        await ctx.send(
            "Sorry, only authorised users can use this command.", ephemeral=True
        )
    else:
        await ctx.send("Shutting down...")
        print("Closing!")
        await bot.close()


@bot.tree.command(
    name="reload_cog",
    description="Reloads a specified cog. Usable only by authorised users",
)
async def reload_cog(interaction: discord.Interaction, cog_name: str):
    if interaction.user.id not in SHUTDOWN_IDS:
        await interaction.response.send_message(
            "Sorry, only authorised users can use this.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"Restarting {cog_name}...", ephemeral=True
        )
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
